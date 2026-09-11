import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

const DB_NAME = 'kumify-offline'
const STORE_NAME = 'queue'
let _db = null

async function getDB() {
  if (_db) return _db
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = e => {
      e.target.result.createObjectStore(STORE_NAME, { keyPath: 'localId' })
    }
    req.onsuccess = e => { _db = e.target.result; resolve(_db) }
    req.onerror = e => reject(e.target.error)
  })
}

async function dbGetAll() {
  const db = await getDB()
  return new Promise((resolve, reject) => {
    const req = db.transaction(STORE_NAME).objectStore(STORE_NAME).getAll()
    req.onsuccess = e => resolve(e.target.result)
    req.onerror = e => reject(e.target.error)
  })
}

async function dbAdd(item) {
  const db = await getDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).add(item)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

async function dbDelete(localId) {
  const db = await getDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).delete(localId)
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export const useOfflineStore = defineStore('offline', () => {
  const queue = ref([])
  const syncing = ref(false)

  async function load() {
    queue.value = await dbGetAll()
  }

  async function enqueue(entry) {
    const item = { localId: crypto.randomUUID(), createdAt: Date.now(), ...entry }
    await dbAdd(item)
    queue.value = [...queue.value, item]
  }

  async function sync() {
    if (syncing.value || queue.value.length === 0) return
    if (!localStorage.getItem('authToken')) return
    syncing.value = true
    for (const item of [...queue.value]) {
      try {
        await api.post(item.endpoint, item.payload)
        await dbDelete(item.localId)
        queue.value = queue.value.filter(q => q.localId !== item.localId)
      } catch (e) {
        if (e instanceof TypeError) break
        await dbDelete(item.localId)
        queue.value = queue.value.filter(q => q.localId !== item.localId)
      }
    }
    syncing.value = false
  }

  return { queue, syncing, count: computed(() => queue.value.length), load, enqueue, sync }
})
