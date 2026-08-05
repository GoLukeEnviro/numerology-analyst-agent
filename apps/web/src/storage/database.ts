import Dexie, { type EntityTable } from "dexie";

import type { EncryptedPayload, VaultMetadata } from "./crypto";

export interface LegacyProfileRecord {
    id: string;
    calculationHash: string;
    createdAt: number;
    updatedAt: number;
    payload: string;
}

export interface StoredProfileRecord {
    schemaVersion: 2 | 3;
    id: string;
    calculationHash: string;
    createdAt: number;
    updatedAt: number;
    protected: boolean;
    payload: string | EncryptedPayload;
}

export interface LocalRunRecord {
    id: string;
    profileId: string;
    createdAt: number;
    payload: string | EncryptedPayload;
}

export interface LocalReportRecord {
    reportId: string;
    profileId: string;
    reportContentHash: string;
    generationContextHash: string;
    methodVersion: string;
    reportSchemaVersion: string;
    calculationHash: string;
    createdAt: number;
    payload: string | EncryptedPayload;
}

export interface LocalThreadRecord {
    id: string;
    profileId: string;
    reportId?: string;
    updatedAt: number;
    payload: string | EncryptedPayload;
}

export interface LocalNoteRecord {
    id: string;
    profileId: string;
    reportId?: string;
    updatedAt: number;
    payload: string | EncryptedPayload;
}

export interface MetaRecord {
    key: string;
    value: VaultMetadata | string | number;
}

export function migrateLegacyProfile(
    record: LegacyProfileRecord,
): StoredProfileRecord {
    return {
        ...record,
        schemaVersion: 2,
        protected: false,
    };
}

export class NumraDatabase extends Dexie {
    profiles!: EntityTable<StoredProfileRecord, "id">;
    runs!: EntityTable<LocalRunRecord, "id">;
    reports!: EntityTable<LocalReportRecord, "reportId">;
    threads!: EntityTable<LocalThreadRecord, "id">;
    notes!: EntityTable<LocalNoteRecord, "id">;
    meta!: EntityTable<MetaRecord, "key">;

    constructor(name = "numra-local-v2") {
        super(name);
        this.version(1).stores({
            profiles: "id,calculationHash,createdAt,updatedAt",
            runs: "id,profileId,createdAt",
            reports: "id,profileId,createdAt",
            threads: "id,profileId,updatedAt",
            notes: "id,profileId,reportId,updatedAt",
        });
        this.version(2)
            .stores({
                profiles: "id,calculationHash,createdAt,updatedAt",
                runs: "id,profileId,createdAt",
                reports: "id,profileId,createdAt",
                threads: "id,profileId,updatedAt",
                notes: "id,profileId,reportId,updatedAt",
                meta: "key",
            })
            .upgrade(async (transaction) => {
                await transaction
                    .table<LegacyProfileRecord, string>("profiles")
                    .toCollection()
                    .modify((record) => {
                        Object.assign(record, migrateLegacyProfile(record));
                    });
            });
        this.version(3)
            .stores({
                profiles: "id,calculationHash,createdAt,updatedAt",
                runs: "id,profileId,createdAt",
                reports: "id,profileId,createdAt",
                threads: "id,profileId,updatedAt",
                notes: "id,profileId,reportId,updatedAt",
                meta: "key",
            })
            .upgrade(async (transaction) => {
                await transaction
                    .table<StoredProfileRecord, string>("profiles")
                    .toCollection()
                    .modify((record) => {
                        record.schemaVersion = 3;
                    });
            });
        this.version(4)
            .stores({
                profiles: "id,calculationHash,createdAt,updatedAt",
                runs: "id,profileId,createdAt",
                reports:
                    "reportId,profileId,calculationHash,reportContentHash,methodVersion,createdAt",
                threads: "id,profileId,reportId,updatedAt",
                notes: "id,profileId,reportId,updatedAt",
                meta: "key",
            })
            .upgrade(async (transaction) => {
                // Migrate existing reports: copy id → reportId, set defaults.
                const oldReports = await transaction
                    .table<
                        {
                            id: string;
                            profileId: string;
                            createdAt: number;
                            payload: unknown;
                        },
                        string
                    >("reports")
                    .toArray();
                await transaction.table("reports").clear();
                for (const r of oldReports) {
                    await transaction.table("reports").add({
                        reportId: r.id,
                        profileId: r.profileId,
                        reportContentHash: "",
                        generationContextHash: "",
                        methodVersion: "v1",
                        reportSchemaVersion: "analysis-report-v2",
                        calculationHash: "",
                        createdAt: r.createdAt,
                        payload: r.payload,
                    });
                }
            });
    }
}

export const numraDatabase = new NumraDatabase();
