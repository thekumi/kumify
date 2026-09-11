import { b64encode, b64decode } from "./util.js";
import { importPublicKey } from "./device.js";

const KEY_ALGO = { name: "AES-GCM", length: 256 };
const ECDH_ALGO = { name: "ECDH", namedCurve: "P-256" };

export async function generateDataKey() {
  // extractable: true — required so the key can be wrapped for other devices
  return crypto.subtle.generateKey(KEY_ALGO, true, ["encrypt", "decrypt", "wrapKey", "unwrapKey"]);
}

// Wrap dataKey for a recipient device using an ephemeral ECDH key pair.
// The recipient unwraps using their device private key + the ephemeral public key.
export async function wrapDataKey(dataKey, recipientPublicKey) {
  const ephemeral = await crypto.subtle.generateKey(ECDH_ALGO, true, ["deriveKey"]);

  const wrappingKey = await crypto.subtle.deriveKey(
    { name: "ECDH", public: recipientPublicKey },
    ephemeral.privateKey,
    KEY_ALGO,
    false,
    ["wrapKey"]
  );

  const iv = crypto.getRandomValues(new Uint8Array(12));
  const wrapped = await crypto.subtle.wrapKey("raw", dataKey, wrappingKey, {
    name: "AES-GCM",
    iv,
  });

  const epkSpki = await crypto.subtle.exportKey("spki", ephemeral.publicKey);

  return JSON.stringify({
    v: 1,
    epk: b64encode(epkSpki),
    iv: b64encode(iv),
    wrapped: b64encode(wrapped),
  });
}

// Unwrap the data key stored on the server using this device's private key.
export async function unwrapDataKey(encryptedDataKeyJson, devicePrivateKey) {
  const { v, epk, iv, wrapped } = JSON.parse(encryptedDataKeyJson);
  if (v !== 1) throw new Error(`Unsupported key format version: ${v}`);

  const ephemeralPublicKey = await importPublicKey(epk);

  const unwrappingKey = await crypto.subtle.deriveKey(
    { name: "ECDH", public: ephemeralPublicKey },
    devicePrivateKey,
    KEY_ALGO,
    false,
    ["unwrapKey"]
  );

  // extractable: true — this device may need to re-wrap the key for new devices
  return crypto.subtle.unwrapKey(
    "raw",
    b64decode(wrapped),
    unwrappingKey,
    { name: "AES-GCM", iv: b64decode(iv) },
    KEY_ALGO,
    true,
    ["encrypt", "decrypt", "wrapKey", "unwrapKey"]
  );
}
