// saveEncrypted: re-encrypts the given fields and strips them from the PATCH body
// so only encrypted_payload reaches the server. Non-encrypted fields pass through.
//
// encryptedFields: array of field names that live in encrypted_payload
// rawRecord:       the original record object (must have .encrypted_payload to detect encryption)
// ks:              useKeystoreStore()
export async function saveEncrypted(updateFn, id, payload, encryptedFields, rawRecord, ks) {
  if (rawRecord?.encrypted_payload) {
    const toEncrypt = {}
    for (const field of encryptedFields) {
      const v = payload[field]
      if (v !== null && v !== undefined && v !== '') toEncrypt[field] = String(v)
    }
    const encrypted_payload = await ks.encryptPayload(toEncrypt)
    const patched = { ...payload, encrypted_payload }
    for (const field of encryptedFields) delete patched[field]
    return updateFn(id, patched)
  }
  return updateFn(id, payload)
}
