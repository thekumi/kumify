import { apiFetch, b64encode } from './util.js'
import { encryptPayload, decryptPayload } from './fields.js'

const MODEL_FIELDS = {
  statuses:     ['title', 'text'],
  moods:        ['name', 'value', 'color', 'icon'],
  activities:   ['name', 'icon'],
  dreams:       ['title', 'content'],
  cbt_records:  ['title', 'situation', 'thoughts', 'pro_facts', 'con_facts', 'realistic', 'outcome'],
  health_logs:  ['notes'],
  vaccinations: ['name', 'target_disease', 'administered_on', 'next_due', 'provider', 'batch_number', 'notes'],
  people:       ['name', 'nickname', 'birthday', 'email', 'phone', 'relationship', 'address', 'notes', 'last_contact'],
  medications:        ['name', 'remarks'],
  health_parameters:  ['name', 'unit', 'icon'],
  habits:             ['name', 'description'],
  habit_logs:   ['note'],
}

const MEDIA_ENDPOINTS = [
  ['status_media', id => `/api/media/status/${id}/`],
  ['dream_media',  id => `/api/media/dream/${id}/`],
]

async function encryptMediaItem(dataKey, url, endpoint) {
  const fileRes = await fetch(url)
  const bytes = await fileRes.arrayBuffer()
  const mime = fileRes.headers.get('content-type') || 'application/octet-stream'
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, dataKey, bytes)
  const ep = { v: 1, iv: b64encode(iv), mime }
  const fname = url.split('/').pop() || 'file'
  const form = new FormData()
  form.append('file', new Blob([ct], { type: 'application/octet-stream' }), fname)
  form.append('encrypted_payload', JSON.stringify(ep))
  const r = await apiFetch('PATCH', endpoint, form)
  return r.ok
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

    const statusUpgrades = staging['status_upgrades'] ?? []
    const upgrades = staging['vaccination_upgrades'] ?? []
    const healthRecords = staging['health_records'] ?? []
    const gpsPending = staging['gps_pending'] ?? 0
    const mediaItems = MEDIA_ENDPOINTS.flatMap(([key]) => staging[key] ?? [])
    const profileUpgrade = staging['profile_upgrade'] ?? null
    const medicalInfoUpgrade = staging['medical_info_upgrade'] ?? null
    const totalFetched = Object.keys(MODEL_FIELDS)
      .reduce((n, key) => n + (staging[key]?.length ?? 0), 0)
      + statusUpgrades.length
      + upgrades.length
      + healthRecords.length
      + gpsPending
      + mediaItems.length
      + (profileUpgrade ? 1 : 0)
      + (medicalInfoUpgrade ? 1 : 0)
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

    // Status upgrade pass: merge plaintext mood FK and activity associations into encrypted payload.
    if (statusUpgrades.length) {
      patch['status_upgrades'] = []
      for (const record of statusUpgrades) {
        if (!record.encrypted_payload) continue
        const existing = await decryptPayload(dataKey, record.encrypted_payload).catch(() => ({}))
        if (record.mood != null) existing['mood_id'] = String(record.mood)
        const actIds = (record.activities ?? []).map(a => a.id)
        if (actIds.length) existing['activity_ids'] = JSON.stringify(actIds)
        patch['status_upgrades'].push({
          id: record.id,
          encrypted_payload: await encryptPayload(dataKey, existing),
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

    // Health record values: each record's value is encrypted and the plaintext cleared.
    if (healthRecords.length) {
      patch['health_records'] = []
      for (const record of healthRecords) {
        patch['health_records'].push({
          id: record.id,
          encrypted_payload: await encryptPayload(dataKey, { value: String(record.value) }),
        })
        batchCount++
      }
    }

    if (profileUpgrade) {
      const plain = {}
      for (const field of ['legal_name', 'phone', 'address', 'date_of_birth']) {
        const v = profileUpgrade[field]
        if (v !== null && v !== undefined && v !== '') plain[field] = String(v)
      }
      if (Object.keys(plain).length) {
        patch.profile_upgrade = {
          id: profileUpgrade.id,
          encrypted_payload: await encryptPayload(dataKey, plain),
        }
        batchCount++
      }
    }

    if (medicalInfoUpgrade) {
      const plain = {}
      for (const field of ['blood_type', 'allergies', 'medical_notes']) {
        const v = medicalInfoUpgrade[field]
        if (v !== null && v !== undefined && v !== '') plain[field] = String(v)
      }
      if (Object.keys(plain).length) {
        patch.medical_info_upgrade = {
          id: medicalInfoUpgrade.id,
          encrypted_payload: await encryptPayload(dataKey, plain),
        }
        batchCount++
      }
    }

    // GPS points: server-side encryption triggered by flag (server holds user's public key).
    if (gpsPending > 0) {
      patch['encrypt_gps'] = true
      batchCount += gpsPending
    }

    // Media encryption: each file is fetched, AES-GCM encrypted, and PATCHed individually.
    let mediaCount = 0
    for (const [key, makeEndpoint] of MEDIA_ENDPOINTS) {
      for (const item of (staging[key] ?? [])) {
        try {
          const ok = await encryptMediaItem(dataKey, item.url, makeEndpoint(item.id))
          if (ok) mediaCount++
        } catch (e) {
          console.warn('[staging] media encryption failed for', key, item.id, e)
        }
      }
    }

    if (batchCount === 0 && mediaCount === 0) break

    let stagingUpdated = 0
    if (batchCount > 0) {
      const patchRes = await apiFetch('PATCH', '/api/staging/', patch)
      if (!patchRes.ok && patchRes.status !== 207) {
        console.warn('[staging] PATCH failed:', patchRes.status)
        break
      }
      stagingUpdated = (await patchRes.json()).updated ?? 0
    }
    totalUpdated += stagingUpdated + mediaCount
  }

  return totalUpdated
}
