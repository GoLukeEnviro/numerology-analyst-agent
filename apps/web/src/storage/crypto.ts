const PBKDF2_ITERATIONS = 600_000;
const AUTO_LOCK_MS = 15 * 60 * 1_000;
const encoder = new TextEncoder();
const decoder = new TextDecoder();

export interface EncryptedPayload {
  version: 1;
  iv: string;
  ciphertext: string;
}

export interface VaultMetadata {
  version: 1;
  salt: string;
  verifier: EncryptedPayload;
}

export interface EncryptedArchive {
  format: "numra-export-v1";
  kdf: {
    algorithm: "PBKDF2-HMAC-SHA256";
    iterations: 600000;
    salt: string;
  };
  cipher: {
    algorithm: "AES-GCM-256";
    iv: string;
    ciphertext: string;
  };
}

export function parseEncryptedArchive(value: unknown): EncryptedArchive {
  if (
    typeof value !== "object" ||
    value === null ||
    !("format" in value) ||
    value.format !== "numra-export-v1" ||
    !("kdf" in value) ||
    typeof value.kdf !== "object" ||
    value.kdf === null ||
    !("cipher" in value) ||
    typeof value.cipher !== "object" ||
    value.cipher === null
  ) {
    throw new Error("Ungültiges Numra-Archiv.");
  }
  return value as EncryptedArchive;
}

export class VaultLockedError extends Error {
  constructor() {
    super("Der lokale Numra-Speicher ist gesperrt.");
    this.name = "VaultLockedError";
  }
}

function toBase64(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function fromBase64(value: string): Uint8Array<ArrayBuffer> {
  const binary = atob(value);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function deriveKey(passphrase: string, salt: Uint8Array<ArrayBuffer>): Promise<CryptoKey> {
  if (passphrase.length < 12) {
    throw new Error("Die Passphrase muss mindestens 12 Zeichen lang sein.");
  }
  const material = await crypto.subtle.importKey(
    "raw",
    encoder.encode(passphrase),
    "PBKDF2",
    false,
    ["deriveKey"],
  );
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      hash: "SHA-256",
      salt,
      iterations: PBKDF2_ITERATIONS,
    },
    material,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

async function encryptWithKey(value: unknown, key: CryptoKey): Promise<EncryptedPayload> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    encoder.encode(JSON.stringify(value)),
  );
  return {
    version: 1,
    iv: toBase64(iv),
    ciphertext: toBase64(new Uint8Array(ciphertext)),
  };
}

async function decryptWithKey<T>(payload: EncryptedPayload, key: CryptoKey): Promise<T> {
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: fromBase64(payload.iv) },
    key,
    fromBase64(payload.ciphertext),
  );
  return JSON.parse(decoder.decode(plaintext)) as T;
}

export async function encryptArchive(
  value: unknown,
  passphrase: string,
): Promise<EncryptedArchive> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const encrypted = await encryptWithKey(value, await deriveKey(passphrase, salt));
  return {
    format: "numra-export-v1",
    kdf: {
      algorithm: "PBKDF2-HMAC-SHA256",
      iterations: PBKDF2_ITERATIONS,
      salt: toBase64(salt),
    },
    cipher: {
      algorithm: "AES-GCM-256",
      iv: encrypted.iv,
      ciphertext: encrypted.ciphertext,
    },
  };
}

export async function decryptArchive<T>(
  archive: EncryptedArchive,
  passphrase: string,
): Promise<T> {
  if (
    archive.format !== "numra-export-v1" ||
    archive.kdf.algorithm !== "PBKDF2-HMAC-SHA256" ||
    archive.kdf.iterations !== PBKDF2_ITERATIONS ||
    archive.cipher.algorithm !== "AES-GCM-256"
  ) {
    throw new Error("Nicht unterstütztes oder manipuliertes Numra-Archiv.");
  }
  const key = await deriveKey(passphrase, fromBase64(archive.kdf.salt));
  return decryptWithKey<T>(
    {
      version: 1,
      iv: archive.cipher.iv,
      ciphertext: archive.cipher.ciphertext,
    },
    key,
  );
}

export class MemoryVault {
  private key: CryptoKey | null = null;
  private lastActivity = 0;
  private enabled = false;

  async initialize(passphrase: string, now = Date.now()): Promise<VaultMetadata> {
    const salt = crypto.getRandomValues(new Uint8Array(16));
    this.key = await deriveKey(passphrase, salt);
    this.enabled = true;
    this.lastActivity = now;
    return {
      version: 1,
      salt: toBase64(salt),
      verifier: await encryptWithKey({ marker: "numra-vault-v1" }, this.key),
    };
  }

  async unlock(passphrase: string, metadata: VaultMetadata, now = Date.now()): Promise<void> {
    const candidate = await deriveKey(passphrase, fromBase64(metadata.salt));
    const verifier = await decryptWithKey<{ marker: string }>(metadata.verifier, candidate);
    if (verifier.marker !== "numra-vault-v1") throw new Error("Ungültige Passphrase.");
    this.key = candidate;
    this.enabled = true;
    this.lastActivity = now;
  }

  lock(): void {
    this.key = null;
  }

  isLocked(): boolean {
    return this.enabled && this.key === null;
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  touch(now = Date.now()): void {
    if (this.key !== null) this.lastActivity = now;
  }

  autoLockIfIdle(now = Date.now()): boolean {
    if (this.key !== null && now - this.lastActivity >= AUTO_LOCK_MS) {
      this.lock();
      return true;
    }
    return false;
  }

  async encrypt(value: unknown, now = Date.now()): Promise<EncryptedPayload> {
    if (this.key === null) throw new VaultLockedError();
    this.lastActivity = now;
    return encryptWithKey(value, this.key);
  }

  async decrypt<T>(payload: EncryptedPayload, now = Date.now()): Promise<T> {
    if (this.key === null) throw new VaultLockedError();
    this.lastActivity = now;
    return decryptWithKey<T>(payload, this.key);
  }
}
