import { b64encode, b64decode } from "./util.js";

const ALGO = { name: "ECDH", namedCurve: "P-256" };

export async function generateDeviceKeyPair() {
  return crypto.subtle.generateKey(
    ALGO,
    false, // private key non-extractable
    ["deriveKey"]
  );
}

export async function exportPublicKey(publicKey) {
  const spki = await crypto.subtle.exportKey("spki", publicKey);
  return b64encode(spki);
}

export async function importPublicKey(spkiBase64) {
  return crypto.subtle.importKey("spki", b64decode(spkiBase64), ALGO, false, []);
}

// Short human-readable fingerprint of a device's public key for out-of-band verification.
// Format: XXXX-XXXX-XXXX (first 6 bytes of SHA-256, uppercase hex, hyphen-separated).
export async function computeDeviceFingerprint(spkiBase64) {
  const bytes = b64decode(spkiBase64)
  const hash = await crypto.subtle.digest('SHA-256', bytes)
  const hex = Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
  return `${hex.slice(0, 4).toUpperCase()}-${hex.slice(4, 8).toUpperCase()}-${hex.slice(8, 12).toUpperCase()}`
}
