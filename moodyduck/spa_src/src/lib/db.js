import { ref } from 'vue'

export const dbVersionError = ref(false)

const DB_NAME = 'moodyduck-data'
const DB_VERSION = 3

const STORES = [
  'statuses',
  'moods',
  'activities',
  'activity_categories',
  'dreams',
  'habits',
  'health_logs',
  'cbt_records',
  'health_parameters',
  'medications',
  'vaccinations',
  'people',
  'properties',
  'sync_meta',
]

let _db = null

function openDB() {
  if (_db) return Promise.resolve(_db)
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = e => {
      const db = e.target.result
      for (const name of STORES) {
        if (db.objectStoreNames.contains(name)) continue
        const store = db.createObjectStore(name, { keyPath: 'id' })
        if (name !== 'sync_meta') {
          store.createIndex('updated_at', 'updated_at', { unique: false })
        }
      }
    }
    req.onsuccess = e => { _db = e.target.result; resolve(_db) }
    req.onerror = e => {
      if (e.target.error?.name === 'VersionError') dbVersionError.value = true
      reject(e.target.error)
    }
  })
}

export async function dbGetAll(storeName) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const req = db.transaction(storeName).objectStore(storeName).getAll()
    req.onsuccess = e => resolve(e.target.result)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbGet(storeName, id) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const req = db.transaction(storeName).objectStore(storeName).get(id)
    req.onsuccess = e => resolve(e.target.result ?? null)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbPut(storeName, item) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    tx.objectStore(storeName).put(item)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function dbPutMany(storeName, items) {
  if (!items.length) return
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    const store = tx.objectStore(storeName)
    for (const item of items) store.put(item)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function dbDelete(storeName, id) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    tx.objectStore(storeName).delete(id)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function dbDeleteMany(storeName, ids) {
  if (!ids.length) return
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    const store = tx.objectStore(storeName)
    for (const id of ids) store.delete(id)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function dbClear(storeName) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    tx.objectStore(storeName).clear()
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function getSyncMeta(key) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const req = db.transaction('sync_meta').objectStore('sync_meta').get(key)
    req.onsuccess = e => resolve(e.target.result?.value ?? null)
    req.onerror = e => reject(e.target.error)
  })
}

export async function setSyncMeta(key, value) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('sync_meta', 'readwrite')
    tx.objectStore('sync_meta').put({ id: key, value })
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}
