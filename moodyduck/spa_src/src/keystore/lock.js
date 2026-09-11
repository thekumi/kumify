import { b64encode, b64decode } from './util.js'

async function deriveLockKey(pin, saltB64) {
  const keyMaterial = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(pin), 'PBKDF2', false, ['deriveKey']
  )
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt: b64decode(saltB64), iterations: 600_000, hash: 'SHA-256' },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['wrapKey', 'unwrapKey']
  )
}

export async function wrapDataKeyForLock(dataKey, pin) {
  const saltBytes = crypto.getRandomValues(new Uint8Array(16))
  const lock_salt = b64encode(saltBytes)
  const lockKey = await deriveLockKey(pin, lock_salt)
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const wrapped = await crypto.subtle.wrapKey('raw', dataKey, lockKey, { name: 'AES-GCM', iv })
  return {
    lock_salt,
    lock_wrapped: JSON.stringify({ iv: b64encode(iv), wrapped: b64encode(wrapped) }),
  }
}

// Throws on wrong PIN (AES-GCM authentication tag mismatch).
export async function unwrapDataKeyFromLock(lockWrapped, lockSalt, pin) {
  const lockKey = await deriveLockKey(pin, lockSalt)
  const { iv, wrapped } = JSON.parse(lockWrapped)
  return crypto.subtle.unwrapKey(
    'raw',
    b64decode(wrapped),
    lockKey,
    { name: 'AES-GCM', iv: b64decode(iv) },
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt', 'wrapKey', 'unwrapKey']
  )
}
