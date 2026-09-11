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
