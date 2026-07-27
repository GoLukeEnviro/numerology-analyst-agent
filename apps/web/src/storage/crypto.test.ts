import { describe, expect, it } from "vitest";

import {
  MemoryVault,
  VaultLockedError,
  decryptArchive,
  encryptArchive,
} from "./crypto";

describe("Numra encryption", () => {
  it("exports authenticated PBKDF2/AES-GCM envelopes", async () => {
    const archive = await encryptArchive({ profiles: [{ id: "p1" }] }, "correct horse");

    expect(archive.format).toBe("numra-export-v2");
    expect(archive.kdf).toEqual(
      expect.objectContaining({
        algorithm: "PBKDF2-HMAC-SHA256",
        iterations: 600_000,
      }),
    );
    expect(archive.cipher.algorithm).toBe("AES-GCM-256");
    await expect(decryptArchive(archive, "correct horse")).resolves.toEqual({
      profiles: [{ id: "p1" }],
    });
    await expect(decryptArchive(archive, "wrong")).rejects.toThrow();
  });

  it("keeps the key in memory and locks after fifteen idle minutes", async () => {
    const vault = new MemoryVault();
    const metadata = await vault.initialize("a long local passphrase", 1_000);
    const encrypted = await vault.encrypt({ name: "Max Mustermann" }, 1_001);

    vault.lock();
    await expect(vault.decrypt(encrypted, 1_002)).rejects.toBeInstanceOf(VaultLockedError);
    await vault.unlock("a long local passphrase", metadata, 2_000);
    await expect(vault.decrypt(encrypted, 2_001)).resolves.toEqual({
      name: "Max Mustermann",
    });

    expect(vault.autoLockIfIdle(2_000 + 15 * 60 * 1_000 + 1)).toBe(true);
    expect(vault.isLocked()).toBe(true);
  });
});
