import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDeviceRecord, putDeviceRecord, clearDeviceRecord } from '@/keystore/db'
import { generateDeviceKeyPair, exportPublicKey, importPublicKey } from '@/keystore/device'
import { generateDataKey, wrapDataKey, unwrapDataKey } from '@/keystore/datakey'
import { unwrapDataKeyFromBackup } from '@/keystore/backup'
import { decryptPayload, encryptPayload } from '@/keystore/fields'
import {
  generateUserKeyPair,
  exportUserPublicKey,
  wrapUserPrivateKey,
  unwrapUserPrivateKey,
} from '@/keystore/userkey'
import { apiFetch } from '@/keystore/util'
import { runStaging } from '@/keystore/staging'
import { wrapDataKeyForLock, unwrapDataKeyFromLock } from '@/keystore/lock'

const AUTOLOCK_KEY = 'ks:autolock-minutes'

export const useKeystoreStore = defineStore('keystore', () => {
  const dataKey = ref(null)
  const userPrivateKey = ref(null)
  const myDeviceId = ref(null)
  // idle | booting | needs_passphrase | waiting | ready | failed | locked
  const status = ref('idle')
  // Set when status === 'needs_passphrase'; holds { encrypted_data_key, kdf_salt }
  const backupPayload = ref(null)
  // True when a PIN-wrapped key is stored in IndexedDB
  const lockConfigured = ref(false)

  let _passphraseResolve = null
  let _passphraseReject = null
  let _autoLockTimer = null
  let _autoLockListening = false

  async function _registerDevice() {
    const keyPair = await generateDeviceKeyPair()
    const publicKeyB64 = await exportPublicKey(keyPair.publicKey)
    const label = navigator.userAgent.substring(0, 255)
    const res = await apiFetch('POST', '/api/devices/', { public_key: publicKeyB64, label })
    if (!res.ok) throw new Error('Device registration failed')
    const device = await res.json()
    const record = {
      device_id: device.device_id,
      private_key: keyPair.privateKey,
      public_key_b64: publicKeyB64,
      data_key: null,
    }
    await putDeviceRecord(record)
    return record
  }

  async function _wrapAndRegister(record, key) {
    const myPublicKey = await importPublicKey(record.public_key_b64)
    const wrapped = await wrapDataKey(key, myPublicKey)
    await apiFetch('PATCH', `/api/devices/${record.device_id}/key/`, { encrypted_data_key: wrapped })
  }

  async function _obtainDataKey(record, deviceState) {
    if (deviceState.encrypted_data_key) {
      const key = await unwrapDataKey(deviceState.encrypted_data_key, record.private_key)
      await _wrapAndRegister(record, key)
      return key
    }

    const backupRes = await apiFetch('GET', '/api/keybackup/')
    if (backupRes.ok) {
      const backup = await backupRes.json()
      backupPayload.value = backup
      status.value = 'needs_passphrase'
      // Suspend until submitPassphrase() is called by the UI
      return new Promise((resolve, reject) => {
        _passphraseResolve = async (passphrase) => {
          const key = await unwrapDataKeyFromBackup(
            backup.encrypted_data_key,
            backup.kdf_salt,
            passphrase
          )
          await _wrapAndRegister(record, key)
          resolve(key)
        }
        _passphraseReject = reject
      })
    }

    const devicesRes = await apiFetch('GET', '/api/devices/')
    if (devicesRes.ok) {
      const { results: devices } = await devicesRes.json()
      const othersWithKey = devices.filter(
        (d) => d.device_id !== record.device_id && d.has_data_key
      )
      if (othersWithKey.length > 0) {
        status.value = 'waiting'
        return null
      }
    }

    const key = await generateDataKey()
    await _wrapAndRegister(record, key)
    return key
  }

  async function boot() {
    if (status.value !== 'idle') return
    status.value = 'booting'
    try {
      let record = await getDeviceRecord()
      if (!record) record = await _registerDevice()
      myDeviceId.value = record.device_id

      // If a PIN-wrapped key exists, don't proceed — require PIN to unlock.
      if (record.lock_wrapped) {
        lockConfigured.value = true
        status.value = 'locked'
        return
      }

      let key
      if (record.data_key) {
        // Cached key — verify the device still exists on the server.
        // If not (server reset, different install), re-register transparently.
        const check = await apiFetch('GET', `/api/devices/${record.device_id}/`)
        if (check.ok) {
          key = record.data_key
        } else {
          const newRecord = await _registerDevice()
          await _wrapAndRegister(newRecord, record.data_key)
          newRecord.data_key = record.data_key
          await putDeviceRecord(newRecord)
          record = newRecord
          myDeviceId.value = record.device_id
          key = record.data_key
        }
      } else {
        const deviceRes = await apiFetch('GET', `/api/devices/${record.device_id}/`)
        if (deviceRes.ok) {
          const deviceState = await deviceRes.json()
          key = await _obtainDataKey(record, deviceState)
        } else {
          // Stale IndexedDB entry — clear it and start fresh
          await clearDeviceRecord()
          record = await _registerDevice()
          myDeviceId.value = record.device_id
          key = await _obtainDataKey(record, { encrypted_data_key: null })
        }
        if (key) {
          record = { ...record, data_key: key }
          await putDeviceRecord(record)
        }
      }

      // Migrate old keys that lack wrapKey/unwrapKey usages
      if (key && !key.usages.includes('wrapKey')) {
        try {
          const raw = await crypto.subtle.exportKey('raw', key)
          key = await crypto.subtle.importKey(
            'raw',
            raw,
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt', 'wrapKey', 'unwrapKey']
          )
          record = { ...record, data_key: key }
          await putDeviceRecord(record)
        } catch (e) {
          console.warn('[keystore] Could not migrate data key usages:', e)
        }
      }

      dataKey.value = key

      // Backfill plaintext records that predate client-side encryption.
      // Runs in the background once per browser session; loops in batches of
      // 200 until the server reports no remaining unencrypted records.
      if (key && !sessionStorage.getItem('ks:staged')) {
        sessionStorage.setItem('ks:staged', '1')
        runStaging(key)
          .then(n => { if (n > 0) console.info(`[staging] Encrypted ${n} record(s)`) })
          .catch(e => console.warn('[staging] failed:', e))
      }

      if (key) {
        let userKey
        if (record.user_private_key) {
          userKey = record.user_private_key
        } else {
          const res = await apiFetch('GET', '/api/userkeypair/')
          if (res.ok) {
            const { encrypted_private_key } = await res.json()
            userKey = await unwrapUserPrivateKey(encrypted_private_key, key)
          } else if (res.status === 404) {
            const kp = await generateUserKeyPair()
            const pubB64 = await exportUserPublicKey(kp.publicKey)
            const encPriv = await wrapUserPrivateKey(kp.privateKey, key)
            const createRes = await apiFetch('POST', '/api/userkeypair/', {
              public_key: pubB64,
              encrypted_private_key: encPriv,
            })
            if (createRes.ok) userKey = await unwrapUserPrivateKey(encPriv, key)
          }
          if (userKey) {
            record = { ...record, user_private_key: userKey }
            await putDeviceRecord(record)
          }
        }
        userPrivateKey.value = userKey

        // Distribute key to any pending devices
        const devRes = await apiFetch('GET', '/api/devices/')
        if (devRes.ok) {
          const { results: devices } = await devRes.json()
          for (const device of devices) {
            if (device.device_id === record.device_id || device.has_data_key) continue
            try {
              const recipientKey = await importPublicKey(device.public_key)
              const wrapped = await wrapDataKey(key, recipientKey)
              await apiFetch('PATCH', `/api/devices/${device.device_id}/key/`, {
                encrypted_data_key: wrapped,
              })
            } catch (e) {
              console.warn(`[keystore] Could not distribute key to ${device.device_id}:`, e)
            }
          }
        }
      }

      if (status.value === 'booting') {
        _setupAutoLock()
        status.value = 'ready'
      }
    } catch (e) {
      console.error('[keystore] Boot failed:', e)
      if (status.value === 'booting') status.value = 'failed'
    }
  }

  // Called by the passphrase modal when the user submits a passphrase.
  // Throws on wrong passphrase so the modal can show the error.
  async function submitPassphrase(passphrase) {
    if (!_passphraseResolve) throw new Error('No passphrase prompt pending')
    await _passphraseResolve(passphrase)
    _setupAutoLock()
    status.value = 'ready'
    _passphraseResolve = null
    _passphraseReject = null
  }

  async function decrypt(item) {
    if (!item?.encrypted_payload || !dataKey.value) return item
    try {
      const plain = await decryptPayload(dataKey.value, item.encrypted_payload)
      return { ...item, ...plain }
    } catch (e) {
      console.warn('[keystore] decryptPayload failed for item', item.id, e)
      return item
    }
  }

  async function decryptAll(items) {
    if (!items?.length) return items
    return Promise.all(items.map(decrypt))
  }

  function lock() {
    clearTimeout(_autoLockTimer)
    _autoLockTimer = null
    dataKey.value = null
    userPrivateKey.value = null
    status.value = 'locked'
  }

  // If a lock PIN is configured, unwrap the key from the PIN.
  // If no PIN is configured, re-runs boot() which reads the raw key from IndexedDB.
  // Throws on wrong PIN so the UI can show an error.
  async function unlock(pin) {
    const record = await getDeviceRecord()
    if (record?.lock_wrapped) {
      const key = await unwrapDataKeyFromLock(record.lock_wrapped, record.lock_salt, pin)
      dataKey.value = key
      if (record.user_private_key) userPrivateKey.value = record.user_private_key
      _setupAutoLock()
      status.value = 'ready'
    } else {
      status.value = 'idle'
      await boot()
    }
  }

  // Wrap the current data key with a PIN and store it in IndexedDB.
  // After this, the raw key is never written to IndexedDB again.
  async function setLockPin(pin) {
    if (!dataKey.value) throw new Error('No data key available')
    const { lock_salt, lock_wrapped } = await wrapDataKeyForLock(dataKey.value, pin)
    const record = await getDeviceRecord()
    await putDeviceRecord({ ...record, data_key: null, lock_salt, lock_wrapped })
    lockConfigured.value = true
  }

  // Verify the current PIN, then restore raw key storage and clear the lock.
  // Throws on wrong PIN.
  async function removeLockPin(pin) {
    const record = await getDeviceRecord()
    if (!record?.lock_wrapped) return
    const key = await unwrapDataKeyFromLock(record.lock_wrapped, record.lock_salt, pin)
    await putDeviceRecord({ ...record, data_key: key, lock_salt: null, lock_wrapped: null })
    lockConfigured.value = false
  }

  // Change PIN: verify old PIN, then re-wrap with new PIN.
  // Throws on wrong old PIN.
  async function changeLockPin(oldPin, newPin) {
    const record = await getDeviceRecord()
    if (!record?.lock_wrapped) throw new Error('No lock PIN configured')
    const key = await unwrapDataKeyFromLock(record.lock_wrapped, record.lock_salt, oldPin)
    const { lock_salt, lock_wrapped } = await wrapDataKeyForLock(key, newPin)
    await putDeviceRecord({ ...record, lock_salt, lock_wrapped })
  }

  function _setupAutoLock() {
    if (_autoLockListening) return
    _autoLockListening = true
    document.addEventListener('visibilitychange', () => {
      if (!dataKey.value) return
      if (document.hidden) {
        const raw = localStorage.getItem(AUTOLOCK_KEY) ?? '5'
        if (raw === 'never') return
        const ms = Number(raw) * 60 * 1000
        if (ms === 0) { lock(); return }
        _autoLockTimer = setTimeout(lock, ms)
      } else {
        clearTimeout(_autoLockTimer)
        _autoLockTimer = null
      }
    })
  }

  async function grantKey(device) {
    if (!dataKey.value) throw new Error('No data key available')
    const recipientKey = await importPublicKey(device.public_key)
    const wrapped = await wrapDataKey(dataKey.value, recipientKey)
    const res = await apiFetch('PATCH', `/api/devices/${device.device_id}/key/`, {
      encrypted_data_key: wrapped,
    })
    if (!res.ok) throw new Error('Failed to grant key')
  }

  return {
    dataKey,
    userPrivateKey,
    myDeviceId,
    status,
    backupPayload,
    lockConfigured,
    boot,
    submitPassphrase,
    lock,
    unlock,
    setLockPin,
    removeLockPin,
    changeLockPin,
    decrypt,
    decryptAll,
    grantKey,
    encryptPayload: (fields) => encryptPayload(dataKey.value, fields),
  }
})
