// buildEncryptedPatch: builds the PATCH body for an encrypted record without calling the server.
// Decrypts the existing payload, merges in updated encrypted fields, returns the full patch body.
// Non-encrypted fields in payload pass through unchanged.
export async function buildEncryptedPatch(payload, encryptedFields, rawRecord, ks) {
  if (!rawRecord?.encrypted_payload) return payload
  // Decrypt first so extra keys not in encryptedFields are preserved.
  const decrypted = await ks.decrypt({ encrypted_payload: rawRecord.encrypted_payload })
  const { encrypted_payload: _ep, ...baseFields } = decrypted
  const toEncrypt = { ...baseFields }
  for (const field of encryptedFields) {
    const v = payload[field]
    const filled = Array.isArray(v) ? v.filter(Boolean) : v
    if (filled !== null && filled !== undefined && filled !== '' && !(Array.isArray(filled) && !filled.length)) {
      toEncrypt[field] = filled
    } else {
      delete toEncrypt[field]
    }
  }
  const encrypted_payload = await ks.encryptPayload(toEncrypt)
  const patched = { ...payload, encrypted_payload }
  for (const field of encryptedFields) delete patched[field]
  return patched
}

// saveEncrypted: builds the patch and immediately calls updateFn (backward-compat wrapper).
export async function saveEncrypted(updateFn, id, payload, encryptedFields, rawRecord, ks) {
  const patched = await buildEncryptedPatch(payload, encryptedFields, rawRecord, ks)
  return updateFn(id, patched)
}
