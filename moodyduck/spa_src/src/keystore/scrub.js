import { apiFetch } from './util.js'
import { encryptPayload, decryptPayload } from './fields.js'
import { runStaging } from './staging.js'

// Returns per-model counts of encrypted records that still hold plaintext.
// Returns null on fetch failure.
export async function checkScrub() {
  const res = await apiFetch('GET', '/api/scrub/')
  if (!res.ok) return null
  const data = await res.json()
  return Object.fromEntries(Object.entries(data).map(([k, v]) => [k, v.length]))
}

// 1. Encrypts any fully-unencrypted records via staging.
// 2. Fetches partially-encrypted records (encrypted_payload set but plaintext fields remain).
// 3. Decrypts each payload, merges in the residual plaintext fields, re-encrypts.
// 4. PATCHes the merged payloads back; server writes new payload and nulls plaintext.
// Returns { staged, scrubbed } totals.
export async function runScrub(dataKey) {
  const staged = await runStaging(dataKey)

  const res = await apiFetch('GET', '/api/scrub/')
  if (!res.ok) return { staged, scrubbed: 0 }
  const partials = await res.json()

  const patch = {}
  let mergeCount = 0

  for (const [key, records] of Object.entries(partials)) {
    if (!records.length) continue
    patch[key] = []
    for (const record of records) {
      const existing = record.encrypted_payload
        ? await decryptPayload(dataKey, record.encrypted_payload).catch(() => ({}))
        : {}

      // Merge any plaintext fields that are absent from the decrypted payload.
      // Django's .values() returns FK fields as <name>_id (e.g. mood → mood_id),
      // which is already the correct key used when encrypting FKs.
      for (const [field, value] of Object.entries(record)) {
        if (field === 'id' || field === 'encrypted_payload') continue
        if (value === null || value === undefined) continue
        if (!(field in existing)) {
          existing[field] = String(value)
        }
      }

      const newPayload = await encryptPayload(dataKey, existing)

      // Verify the payload round-trips before we commit to nulling the plaintext.
      const verified = await decryptPayload(dataKey, newPayload).catch(() => null)
      if (!verified) {
        console.warn('[scrub] payload verification failed for', key, record.id, '— skipping')
        continue
      }
      const plaintextFields = Object.keys(record).filter(
        f => f !== 'id' && f !== 'encrypted_payload' && record[f] !== null && record[f] !== undefined
      )
      const missing = plaintextFields.filter(f => !(f in verified))
      if (missing.length) {
        console.warn('[scrub] payload missing fields', missing, 'for', key, record.id, '— skipping')
        continue
      }

      patch[key].push({ id: record.id, encrypted_payload: newPayload })
      mergeCount++
    }
  }

  if (mergeCount === 0) return { staged, scrubbed: 0 }

  const patchRes = await apiFetch('PATCH', '/api/scrub/', patch)
  if (!patchRes.ok) return { staged, scrubbed: 0 }
  const data = await patchRes.json()
  return { staged, scrubbed: data.scrubbed ?? 0 }
}
