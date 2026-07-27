import "fake-indexeddb/auto";

import { afterEach, describe, expect, it } from "vitest";

import type { ProfileCalculationResult } from "../api/types";
import type { AnalysisFollowUp, AnalysisReport } from "../api/types";
import { NumraDatabase, migrateLegacyProfile } from "./database";
import { MemoryVault, VaultLockedError, encryptArchive } from "./crypto";
import { LocalProfileRepository } from "./repository";

function profile(name: string, hashCharacter: string): ProfileCalculationResult {
  return {
    deterministic_hash: hashCharacter.repeat(64),
    input_ref: { core_name: name, as_of_date: "2026-07-26" },
  } as unknown as ProfileCalculationResult;
}

const databases: NumraDatabase[] = [];

function repository(vault = new MemoryVault()) {
  const database = new NumraDatabase(`numra-test-${crypto.randomUUID()}`);
  databases.push(database);
  return { database, repository: new LocalProfileRepository(database, vault), vault };
}

afterEach(async () => {
  await Promise.all(databases.splice(0).map(async (database) => database.delete()));
});

describe("LocalProfileRepository", () => {
  it("preserves a stored V2 profile and its historical hash without creating a hybrid", async () => {
    const state = repository();
    const legacy = {
      deterministic_hash: "v".repeat(64),
      input_ref: { core_name: "Legacy V2", as_of_date: "2026-07-26" },
      schema_version: "profile-calculation-result-v2",
      life_path_a: { reduced_value: 1 },
      policy: { master_numbers: [11, 22, 33] },
      maturity: { reduced_value: 6 },
      core_name: {
        basis: "core_name",
        expression: { reduced_value: 5 },
      },
      active_name: {
        basis: "active_name",
        expression: { reduced_value: 7 },
      },
    } as unknown as ProfileCalculationResult;

    const saved = await state.repository.saveProfile(legacy, true);
    const reloaded = await state.repository.getProfile(saved.id);

    expect(reloaded?.profile).toEqual(legacy);
    expect(reloaded?.calculationHash).toBe("v".repeat(64));
    expect(reloaded?.profile.core_name).not.toHaveProperty("maturity");
    expect(reloaded?.profile.active_name).not.toHaveProperty("maturity");
  });

  it("requires explicit opt-in and supports search, sorting and deletion", async () => {
    const { repository: profiles } = repository();
    await expect(profiles.saveProfile(profile("Max Mustermann", "a"), false)).rejects.toThrow(
      /Opt-in/,
    );

    const max = await profiles.saveProfile(profile("Max Mustermann", "a"), true);
    await profiles.saveProfile(profile("Anna Beispiel", "b"), true);

    expect((await profiles.listProfiles({ query: "max", sort: "name" }))[0]?.name).toBe(
      "Max Mustermann",
    );
    expect((await profiles.listProfiles({ query: "", sort: "name" }))[0]?.name).toBe(
      "Anna Beispiel",
    );
    await profiles.deleteProfile(max.id);
    expect(await profiles.getProfile(max.id)).toBeNull();
  });

  it("stores protected payloads without plaintext and requires unlock", async () => {
    const { database, repository: profiles, vault } = repository();
    await profiles.enableProtection("a long local passphrase");
    const saved = await profiles.saveProfile(profile("Secret Name", "c"), true);
    const raw = await database.profiles.get(saved.id);

    expect(JSON.stringify(raw)).not.toContain("Secret Name");
    vault.lock();
    await expect(profiles.getProfile(saved.id)).rejects.toBeInstanceOf(VaultLockedError);
    await profiles.unlock("a long local passphrase");
    await expect(profiles.getProfile(saved.id)).resolves.toEqual(
      expect.objectContaining({ name: "Secret Name" }),
    );
  });

  it("never writes plaintext when a persisted vault is locked after restart", async () => {
    const state = repository();
    await state.repository.enableProtection("a long local passphrase");
    state.repository.lock();

    const restarted = new LocalProfileRepository(state.database, new MemoryVault());
    await expect(
      restarted.saveProfile(profile("Must Stay Secret", "f"), true),
    ).rejects.toBeInstanceOf(VaultLockedError);
    expect(await state.database.profiles.count()).toBe(0);
  });

  it("exports, imports and completely deletes local data", async () => {
    const source = repository();
    await source.repository.saveProfile(profile("Export Name", "d"), true);
    const archive = await source.repository.exportAll("archive passphrase");

    const target = repository();
    await target.repository.importAll(archive, "archive passphrase");
    expect(await target.repository.listProfiles({ query: "", sort: "updated" })).toHaveLength(1);

    await target.repository.deleteAllLocalData();
    expect(await target.database.profiles.count()).toBe(0);
    expect(await target.database.runs.count()).toBe(0);
    expect(await target.database.reports.count()).toBe(0);
    expect(await target.database.threads.count()).toBe(0);
    expect(await target.database.notes.count()).toBe(0);
  });

  it("round-trips every payload from one protected vault into another", async () => {
    const source = repository();
    await source.repository.enableProtection("source vault passphrase");
    const saved = await source.repository.saveProfile(profile("Protected Export", "z"), true);
    const report = { schema_version: "analysis-report-v2", summary: "Protected report" } as AnalysisReport;
    const followUp = { schema_version: "analysis-follow-up-v2", answer: "Protected answer" } as AnalysisFollowUp;
    await source.repository.saveReport(saved.id, report, true);
    await source.repository.saveFollowUp(saved.id, followUp, true);
    await source.repository.saveNote(saved.id, "Protected note", true);
    const archive = await source.repository.exportAll("archive passphrase");

    const target = repository();
    await target.repository.enableProtection("different target passphrase");
    await target.repository.importAll(archive, "archive passphrase");

    expect(await target.repository.getReport(saved.id)).toEqual(report);
    expect(await target.repository.listFollowUps(saved.id)).toEqual([followUp]);
    expect(await target.repository.getNote(saved.id)).toBe("Protected note");
    expect(JSON.stringify(await target.database.reports.toArray())).not.toContain("Protected report");
    expect(JSON.stringify(await target.database.notes.toArray())).not.toContain("Protected note");
  });

  it("migrates an unprotected V1 archive and rejects unrecoverable protected V1 payloads", async () => {
    const legacyProfile = profile("Legacy Export", "l");
    const legacyContents = {
      schemaVersion: 1 as const,
      exportedAt: "2026-07-27T00:00:00.000Z",
      profiles: [legacyProfile],
      runs: [{
        id: "legacy-run",
        profileId: "l".repeat(16),
        createdAt: 1,
        payload: JSON.stringify(legacyProfile),
      }],
      reports: [],
      threads: [],
      notes: [],
    };
    const encrypted = await encryptArchive(legacyContents, "archive passphrase");
    const legacyArchive = { ...encrypted, format: "numra-export-v1" as const };
    const target = repository();

    await target.repository.importAll(legacyArchive, "archive passphrase");
    expect(await target.repository.listProfiles({ query: "", sort: "updated" })).toHaveLength(1);

    const protectedContents = {
      ...legacyContents,
      runs: [{
        ...legacyContents.runs[0],
        payload: { version: 1 as const, iv: "AA==", ciphertext: "AA==" },
      }],
    };
    const protectedEncrypted = await encryptArchive(
      protectedContents,
      "archive passphrase",
    );
    await expect(
      repository().repository.importAll(
        { ...protectedEncrypted, format: "numra-export-v1" },
        "archive passphrase",
      ),
    ).rejects.toThrow(/ursprünglichen.*entsperrten Vault/i);
  });

  it("recovers protected V1 payloads inside their original unlocked vault", async () => {
    const source = repository();
    await source.repository.enableProtection("source vault passphrase");
    const saved = await source.repository.saveProfile(profile("Protected V1", "p"), true);
    const report = {
      schema_version: "analysis-report-v2",
      summary: "Legacy protected report",
    } as AnalysisReport;
    const followUp = {
      schema_version: "analysis-follow-up-v2",
      answer: "Legacy protected answer",
    } as AnalysisFollowUp;
    await source.repository.saveReport(saved.id, report, true);
    await source.repository.saveFollowUp(saved.id, followUp, true);
    await source.repository.saveNote(saved.id, "Legacy protected note", true);

    const legacyContents = {
      schemaVersion: 1 as const,
      exportedAt: "2026-07-27T00:00:00.000Z",
      profiles: [saved.profile],
      runs: await source.database.runs.toArray(),
      reports: await source.database.reports.toArray(),
      threads: await source.database.threads.toArray(),
      notes: await source.database.notes.toArray(),
    };
    const encrypted = await encryptArchive(legacyContents, "archive passphrase");
    const legacyArchive = { ...encrypted, format: "numra-export-v1" as const };

    await source.repository.deleteProfile(saved.id);
    await source.repository.importAll(legacyArchive, "archive passphrase");

    expect(await source.repository.getReport(saved.id)).toEqual(report);
    expect(await source.repository.listFollowUps(saved.id)).toEqual([followUp]);
    expect(await source.repository.getNote(saved.id)).toBe("Legacy protected note");
  });

  it("migrates legacy profile records to schema version two", () => {
    const migrated = migrateLegacyProfile({
      id: "legacy",
      calculationHash: "e".repeat(64),
      createdAt: 1,
      updatedAt: 1,
      payload: JSON.stringify(profile("Legacy Name", "e")),
    });

    expect(migrated.schemaVersion).toBe(2);
    expect(migrated.protected).toBe(false);
  });

  it("enforces one local report and two local follow-ups per profile", async () => {
    const state = repository();
    const saved = await state.repository.saveProfile(profile("Quota Name", "q"), true);
    const report = { schema_version: "analysis-report-v2" } as AnalysisReport;
    const followUp = { schema_version: "analysis-follow-up-v2" } as AnalysisFollowUp;

    await state.repository.saveReport(saved.id, report, true);
    await expect(state.repository.saveReport(saved.id, report, true)).rejects.toThrow(/einen Bericht/);
    await state.repository.saveFollowUp(saved.id, followUp, true);
    await state.repository.saveFollowUp(saved.id, followUp, true);
    expect(await state.repository.getReport(saved.id)).toEqual(report);
    expect(await state.repository.listFollowUps(saved.id)).toHaveLength(2);
    await expect(state.repository.saveFollowUp(saved.id, followUp, true)).rejects.toThrow(
      /zwei Rückfragen/,
    );
  });

  it("creates, updates and removes a local note for a profile", async () => {
    const state = repository();
    const saved = await state.repository.saveProfile(profile("Note Name", "n"), true);

    await state.repository.saveNote(saved.id, "Eine persönliche Reflexion.", true);
    expect(await state.repository.getNote(saved.id)).toBe("Eine persönliche Reflexion.");
    await state.repository.deleteNote(saved.id);
    expect(await state.repository.getNote(saved.id)).toBeNull();
  });
});
