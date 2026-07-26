import "fake-indexeddb/auto";

import { afterEach, describe, expect, it } from "vitest";

import type { ProfileCalculationResult } from "../api/types";
import type { AnalysisFollowUp, AnalysisReport } from "../api/types";
import { NumraDatabase, migrateLegacyProfile } from "./database";
import { MemoryVault, VaultLockedError } from "./crypto";
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
    const report = { schema_version: "analysis-report-v1" } as AnalysisReport;
    const followUp = { schema_version: "analysis-follow-up-v1" } as AnalysisFollowUp;

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
});
