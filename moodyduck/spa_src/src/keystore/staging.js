import { apiFetch } from './util.js'
import { encryptPayload, decryptPayload } from './fields.js'

const MODEL_FIELDS = {
  statuses:     ['title', 'text'],
  moods:        ['name', 'value', 'color', 'icon'],
  activities:   ['name', 'icon'],
  dreams:       ['title', 'content'],
  cbt_records:  ['title', 'situation', 'thoughts', 'pro_facts', 'con_facts', 'realistic', 'outcome'],
  health_logs:  ['notes'],
  vaccinations: ['name', 'target_disease', 'administered_on', 'next_due', 'provider', 'batch_number', 'notes'],
}

// Encrypts all plaintext records in batches of _STAGING_BATCH (server-side page size).
// Loops until the server returns no more records to encrypt.
export async function runStaging(dataKey) {
  let totalUpdated = 0

  while (true) {
    const res = await apiFetch('GET', '/api/staging/')
    if (!res.ok) {
      console.warn('[staging] GET failed:', res.status)
      break
    }
    const staging = await res.json()

    // Count total fetched across all models; stop when server returns nothing.
    const upgrades = staging['vaccination_upgrades'] ?? []
    const totalFetched = Object.keys(MODEL_FIELDS)
      .reduce((n, key) => n + (staging[key]?.length ?? 0), 0) + upgrades.length
    if (totalFetched === 0) break

    const patch = {}
    let batchCount = 0

    for (const [key, fields] of Object.entries(MODEL_FIELDS)) {
      const records = staging[key] ?? []
      if (!records.length) continue

      patch[key] = []
      for (const record of records) {
        const plain = {}
        for (const field of fields) {
          const v = record[field]
          if (v !== null && v !== undefined && v !== '') plain[field] = String(v)
        }
        if (!Object.keys(plain).length) continue

        patch[key].push({
          id: record.id,
          encrypted_payload: await encryptPayload(dataKey, plain),
        })
        batchCount++
      }
    }

    // Upgrade pass: merge plaintext dates into already-encrypted vaccination payloads.
    if (upgrades.length) {
      patch['vaccination_upgrades'] = []
      for (const record of upgrades) {
        if (!record.encrypted_payload) continue
        const existing = await decryptPayload(dataKey, record.encrypted_payload).catch(() => ({}))
        if (record.administered_on) existing['administered_on'] = record.administered_on
        if (record.next_due) existing['next_due'] = record.next_due
        patch['vaccination_upgrades'].push({
          id: record.id,
          encrypted_payload: await encryptPayload(dataKey, existing),
        })
        batchCount++
      }
    }

    if (batchCount === 0) break  // All fetched records had empty fields — nothing to do.

    const patchRes = await apiFetch('PATCH', '/api/staging/', patch)
    if (!patchRes.ok && patchRes.status !== 207) {
      console.warn('[staging] PATCH failed:', patchRes.status)
      break
    }
    totalUpdated += (await patchRes.json()).updated ?? 0
  }

  return totalUpdated
}
