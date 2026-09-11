import { b64encode, b64decode } from "./util.js";

async function deriveBackupKey(passphrase, saltB64) {
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(passphrase),
    "PBKDF2",
    false,
    ["deriveKey"]
  );
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: b64decode(saltB64),
      iterations: 600_000,
      hash: "SHA-256",
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["wrapKey", "unwrapKey"]
  );
}

// Returns {encrypted_data_key, kdf_salt} ready to POST to /api/keybackup/
export async function wrapDataKeyForBackup(dataKey, passphrase) {
  const saltBytes = crypto.getRandomValues(new Uint8Array(16));
  const kdf_salt = b64encode(saltBytes);
  const backupKey = await deriveBackupKey(passphrase, kdf_salt);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const wrapped = await crypto.subtle.wrapKey("raw", dataKey, backupKey, {
    name: "AES-GCM",
    iv,
  });
  return {
    encrypted_data_key: JSON.stringify({ iv: b64encode(iv), wrapped: b64encode(wrapped) }),
    kdf_salt,
  };
}

// Throws on wrong passphrase (AES-GCM authentication tag mismatch).
export async function unwrapDataKeyFromBackup(encryptedDataKey, kdfSalt, passphrase) {
  const backupKey = await deriveBackupKey(passphrase, kdfSalt);
  const { iv, wrapped } = JSON.parse(encryptedDataKey);
  // extractable: true so this key can be distributed to other devices
  return crypto.subtle.unwrapKey(
    "raw",
    b64decode(wrapped),
    backupKey,
    { name: "AES-GCM", iv: b64decode(iv) },
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
}
