// Client-side media encryption/decryption.
// Encrypted file format: [12-byte IV][AES-256-GCM ciphertext]

export async function encryptFile(dataKey, file) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = await file.arrayBuffer();
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, dataKey, plaintext);
  const out = new Uint8Array(12 + ciphertext.byteLength);
  out.set(iv, 0);
  out.set(new Uint8Array(ciphertext), 12);
  return new Blob([out], { type: "application/octet-stream" });
}

export async function decryptFileBuffer(dataKey, encryptedBuffer) {
  const iv = new Uint8Array(encryptedBuffer, 0, 12);
  const ciphertext = encryptedBuffer.slice(12);
  return crypto.subtle.decrypt({ name: "AES-GCM", iv }, dataKey, ciphertext);
}

export async function decryptMediaUrl(dataKey, url, mimeType) {
  const res = await fetch(url, { credentials: "same-origin" });
  if (!res.ok) throw new Error(`media fetch failed: ${res.status}`);
  const buf = await res.arrayBuffer();
  const plain = await decryptFileBuffer(dataKey, buf);
  return URL.createObjectURL(new Blob([plain], { type: mimeType || "application/octet-stream" }));
}
