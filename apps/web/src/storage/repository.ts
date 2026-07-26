import type {
  AnalysisFollowUp,
  AnalysisReport,
  ProfileCalculationResult,
} from "../api/types";
import {
  type EncryptedArchive,
  type EncryptedPayload,
  MemoryVault,
  VaultLockedError,
  decryptArchive,
  encryptArchive,
} from "./crypto";
import {
  type LocalNoteRecord,
  type LocalReportRecord,
  type LocalRunRecord,
  type LocalThreadRecord,
  type NumraDatabase,
  type StoredProfileRecord,
  numraDatabase,
} from "./database";

const VAULT_META_KEY = "vault";

export interface LocalProfile {
  id: string;
  name: string;
  calculationHash: string;
  createdAt: number;
  updatedAt: number;
  protected: boolean;
  profile: ProfileCalculationResult;
}

export interface ProfileListOptions {
  query: string;
  sort: "name" | "updated";
}

interface ExportContents {
  schemaVersion: 1;
  exportedAt: string;
  profiles: ProfileCalculationResult[];
  runs: LocalRunRecord[];
  reports: LocalReportRecord[];
  threads: LocalThreadRecord[];
  notes: LocalNoteRecord[];
}

function parseProfile(value: string): ProfileCalculationResult {
  return JSON.parse(value) as ProfileCalculationResult;
}

export class LocalProfileRepository {
  constructor(
    readonly database: NumraDatabase = numraDatabase,
    readonly vault = new MemoryVault(),
  ) {}

  async enableProtection(passphrase: string): Promise<void> {
    if ((await this.database.profiles.count()) || (await this.isProtectionEnabled())) {
      throw new Error("Passphraseschutz kann nur für eine leere Bibliothek aktiviert werden.");
    }
    const metadata = await this.vault.initialize(passphrase);
    await this.database.meta.put({ key: VAULT_META_KEY, value: metadata });
  }

  async unlock(passphrase: string): Promise<void> {
    const record = await this.database.meta.get(VAULT_META_KEY);
    if (record === undefined || typeof record.value !== "object") {
      throw new Error("Für diese Bibliothek ist kein Passphraseschutz eingerichtet.");
    }
    await this.vault.unlock(passphrase, record.value);
  }

  lock(): void {
    this.vault.lock();
  }

  touch(): void {
    this.vault.touch();
  }

  autoLockIfIdle(): boolean {
    return this.vault.autoLockIfIdle();
  }

  async isProtectionEnabled(): Promise<boolean> {
    return (await this.database.meta.get(VAULT_META_KEY)) !== undefined;
  }

  async saveProfile(
    profile: ProfileCalculationResult,
    optIn: boolean,
  ): Promise<LocalProfile> {
    if (!optIn) throw new Error("Opt-in ist vor dauerhafter Speicherung erforderlich.");
    const now = Date.now();
    const id = profile.deterministic_hash.slice(0, 16);
    const existing = await this.database.profiles.get(id);
    const protectedPayload = await this.isProtectionEnabled();
    if (protectedPayload && !this.vault.isEnabled()) throw new VaultLockedError();
    const serialized = JSON.stringify(profile);
    const payload = protectedPayload ? await this.vault.encrypt(profile) : serialized;
    const record: StoredProfileRecord = {
      schemaVersion: 2,
      id,
      calculationHash: profile.deterministic_hash,
      createdAt: existing?.createdAt ?? now,
      updatedAt: now,
      protected: protectedPayload,
      payload,
    };
    await this.database.transaction("rw", this.database.profiles, this.database.runs, async () => {
      await this.database.profiles.put(record);
      await this.database.runs.put({
        id: crypto.randomUUID(),
        profileId: id,
        createdAt: now,
        payload,
      });
    });
    return this.decodeProfile(record);
  }

  async getProfile(id: string): Promise<LocalProfile | null> {
    const record = await this.database.profiles.get(id);
    return record === undefined ? null : this.decodeProfile(record);
  }

  async listProfiles(options: ProfileListOptions): Promise<LocalProfile[]> {
    const records = await this.database.profiles.toArray();
    const profiles = await Promise.all(records.map(async (record) => this.decodeProfile(record)));
    const query = options.query.trim().toLocaleLowerCase("de");
    const filtered = profiles.filter((profile) =>
      profile.name.toLocaleLowerCase("de").includes(query),
    );
    filtered.sort((left, right) =>
      options.sort === "name"
        ? left.name.localeCompare(right.name, "de")
        : right.updatedAt - left.updatedAt,
    );
    return filtered;
  }

  async deleteProfile(id: string): Promise<void> {
    await this.database.transaction(
      "rw",
      [
        this.database.profiles,
        this.database.runs,
        this.database.reports,
        this.database.threads,
        this.database.notes,
      ],
      async () => {
        await this.database.profiles.delete(id);
        await Promise.all([
          this.database.runs.where("profileId").equals(id).delete(),
          this.database.reports.where("profileId").equals(id).delete(),
          this.database.threads.where("profileId").equals(id).delete(),
          this.database.notes.where("profileId").equals(id).delete(),
        ]);
      },
    );
  }

  async saveReport(
    profileId: string,
    report: AnalysisReport,
    optIn: boolean,
  ): Promise<void> {
    if (!optIn) throw new Error("Opt-in ist vor dauerhafter Speicherung erforderlich.");
    if ((await this.database.reports.where("profileId").equals(profileId).count()) >= 1) {
      throw new Error("Pro lokalem Profil kann nur einen Bericht gespeichert werden.");
    }
    await this.database.reports.add({
      id: `report:${profileId}`,
      profileId,
      createdAt: Date.now(),
      payload: await this.encodePayload(report),
    });
  }

  async getReport(profileId: string): Promise<AnalysisReport | null> {
    const record = await this.database.reports.where("profileId").equals(profileId).first();
    return record === undefined
      ? null
      : this.decodePayload<AnalysisReport>(record.payload);
  }

  async saveFollowUp(
    profileId: string,
    followUp: AnalysisFollowUp,
    optIn: boolean,
  ): Promise<void> {
    if (!optIn) throw new Error("Opt-in ist vor dauerhafter Speicherung erforderlich.");
    if ((await this.database.threads.where("profileId").equals(profileId).count()) >= 2) {
      throw new Error("Pro lokalem Profil können nur zwei Rückfragen gespeichert werden.");
    }
    await this.database.threads.add({
      id: crypto.randomUUID(),
      profileId,
      updatedAt: Date.now(),
      payload: await this.encodePayload(followUp),
    });
  }

  async listFollowUps(profileId: string): Promise<AnalysisFollowUp[]> {
    const records = await this.database.threads.where("profileId").equals(profileId).sortBy("updatedAt");
    return Promise.all(
      records.map(async (record) => this.decodePayload<AnalysisFollowUp>(record.payload)),
    );
  }

  async saveNote(
    profileId: string,
    text: string,
    optIn: boolean,
    reportId?: string,
  ): Promise<void> {
    if (!optIn) throw new Error("Opt-in ist vor dauerhafter Speicherung erforderlich.");
    const normalized = text.trim();
    if (!normalized || normalized.length > 5_000) {
      throw new Error("Notizen müssen zwischen 1 und 5.000 Zeichen enthalten.");
    }
    const id = `note:${profileId}:${reportId ?? "profile"}`;
    await this.database.notes.put({
      id,
      profileId,
      reportId,
      updatedAt: Date.now(),
      payload: await this.encodePayload(normalized),
    });
  }

  async getNote(profileId: string, reportId?: string): Promise<string | null> {
    const record = await this.database.notes.get(`note:${profileId}:${reportId ?? "profile"}`);
    return record === undefined ? null : this.decodePayload<string>(record.payload);
  }

  async deleteNote(profileId: string, reportId?: string): Promise<void> {
    await this.database.notes.delete(`note:${profileId}:${reportId ?? "profile"}`);
  }

  async deleteAllLocalData(): Promise<void> {
    await this.database.transaction(
      "rw",
      [
        this.database.profiles,
        this.database.runs,
        this.database.reports,
        this.database.threads,
        this.database.notes,
        this.database.meta,
      ],
      async () => {
        await Promise.all([
          this.database.profiles.clear(),
          this.database.runs.clear(),
          this.database.reports.clear(),
          this.database.threads.clear(),
          this.database.notes.clear(),
          this.database.meta.clear(),
        ]);
      },
    );
    this.vault.lock();
  }

  async exportAll(passphrase: string): Promise<EncryptedArchive> {
    const profiles = await this.listProfiles({ query: "", sort: "updated" });
    return encryptArchive(
      {
        schemaVersion: 1,
        exportedAt: new Date().toISOString(),
        profiles: profiles.map((profile) => profile.profile),
        runs: await this.database.runs.toArray(),
        reports: await this.database.reports.toArray(),
        threads: await this.database.threads.toArray(),
        notes: await this.database.notes.toArray(),
      } satisfies ExportContents,
      passphrase,
    );
  }

  async importAll(archive: EncryptedArchive, passphrase: string): Promise<void> {
    const contents = await decryptArchive<ExportContents>(archive, passphrase);
    if (contents.schemaVersion !== 1 || !Array.isArray(contents.profiles)) {
      throw new Error("Ungültiger Numra-Export.");
    }
    for (const profile of contents.profiles) await this.saveProfile(profile, true);
    await this.database.transaction(
      "rw",
      [
        this.database.runs,
        this.database.reports,
        this.database.threads,
        this.database.notes,
      ],
      async () => {
        await this.database.runs.bulkPut(contents.runs);
        await this.database.reports.bulkPut(contents.reports);
        await this.database.threads.bulkPut(contents.threads);
        await this.database.notes.bulkPut(contents.notes);
      },
    );
  }

  private async decodeProfile(record: StoredProfileRecord): Promise<LocalProfile> {
    const profile = record.protected
      ? await this.vault.decrypt<ProfileCalculationResult>(record.payload as EncryptedPayload)
      : parseProfile(record.payload as string);
    return {
      id: record.id,
      name: profile.input_ref.core_name,
      calculationHash: record.calculationHash,
      createdAt: record.createdAt,
      updatedAt: record.updatedAt,
      protected: record.protected,
      profile,
    };
  }

  private async encodePayload(value: unknown): Promise<string | EncryptedPayload> {
    const protectedPayload = await this.isProtectionEnabled();
    if (protectedPayload && !this.vault.isEnabled()) throw new VaultLockedError();
    return protectedPayload ? this.vault.encrypt(value) : JSON.stringify(value);
  }

  private async decodePayload<T>(payload: string | EncryptedPayload): Promise<T> {
    return typeof payload === "string"
      ? (JSON.parse(payload) as T)
      : this.vault.decrypt<T>(payload);
  }
}

export const localProfiles = new LocalProfileRepository();
