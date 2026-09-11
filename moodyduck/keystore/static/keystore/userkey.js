import { b64encode, b64decode } from "./util.js";
import { importPublicKey } from "./device.js";

const ECDH_ALGO = { name: "ECDH", namedCurve: "P-256" };
const AES_ALGO = { name: "AES-GCM", length: 256 };

// extractable: true — private key must be wrappable (pkcs8) with the data key
export async function generateUserKeyPair() {
  return crypto.subtle.generateKey(ECDH_ALGO, true, ["deriveKey"]);
}

export async function exportUserPublicKey(publicKey) {
  const spki = await crypto.subtle.exportKey("spki", publicKey);
  return b64encode(spki);
}

export async function wrapUserPrivateKey(privateKey, dataKey) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const wrapped = await crypto.subtle.wrapKey("pkcs8", privateKey, dataKey, {
    name: "AES-GCM",
    iv,
  });
  return JSON.stringify({ iv: b64encode(iv), wrapped: b64encode(wrapped) });
}

// extractable: false — the private key never leaves the browser after this
export async function unwrapUserPrivateKey(encryptedStr, dataKey) {
  const { iv, wrapped } = JSON.parse(encryptedStr);
  return crypto.subtle.unwrapKey(
    "pkcs8",
    b64decode(wrapped),
    dataKey,
    { name: "AES-GCM", iv: b64decode(iv) },
    ECDH_ALGO,
    false,
    ["deriveKey"]
  );
}

// Decrypt a v:2 ECIES payload produced by keystore/crypto.py.
// Returns the decrypted fields as a plain object.
export async function decryptECIES(userPrivateKey, payload) {
  const { v, epk, iv, wrapped } =
    typeof payload === "string" ? JSON.parse(payload) : payload;
  if (v !== 2) throw new Error(`Unsupported ECIES payload version: ${v}`);

  const ephemeralPublicKey = await importPublicKey(epk);

  // Derive the AES key via ECDH — matches Python's raw shared-secret approach
  const aesKey = await crypto.subtle.deriveKey(
    { name: "ECDH", public: ephemeralPublicKey },
    userPrivateKey,
    AES_ALGO,
    false,
    ["decrypt"]
  );

  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: b64decode(iv) },
    aesKey,
    b64decode(wrapped)
  );

  return JSON.parse(new TextDecoder().decode(plaintext));
}
