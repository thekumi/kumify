import { b64encode, b64decode } from "./util.js";

const enc = new TextEncoder();
const dec = new TextDecoder();

export async function encryptField(dataKey, plaintext) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    dataKey,
    enc.encode(String(plaintext))
  );
  return { ct: b64encode(ct), iv: b64encode(iv) };
}

export async function decryptField(dataKey, ct, iv) {
  const plain = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: b64decode(iv) },
    dataKey,
    b64decode(ct)
  );
  return dec.decode(plain);
}

// Encrypts a {fieldName: value} object into the payload format the server stores.
// Null/undefined/empty-string values are omitted.
export async function encryptPayload(dataKey, fields) {
  const result = { v: 1, fields: {} };
  for (const [name, value] of Object.entries(fields)) {
    if (value !== null && value !== undefined && value !== "") {
      result.fields[name] = await encryptField(dataKey, value);
    }
  }
  return result;
}

// Decrypts a stored payload object back to {fieldName: plaintext}.
// Returns {} if payload is null/missing or an unrecognised version.
export async function decryptPayload(dataKey, payload) {
  if (!payload || payload.v !== 1) return {};
  const result = {};
  for (const [name, { ct, iv }] of Object.entries(payload.fields ?? {})) {
    result[name] = await decryptField(dataKey, ct, iv);
  }
  return result;
}
