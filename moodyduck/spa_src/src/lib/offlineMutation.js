import { api } from '@/api/client'
import { dbPut, dbDelete } from '@/lib/db'
import { useOfflineStore } from '@/stores/offline'
import { buildEncryptedPatch } from '@/keystore/saveEncrypted'

export async function createOrQueue(endpoint, payload, store) {
  const offline = useOfflineStore()
  try {
    const result = await api.post(endpoint, payload)
    if (store) await dbPut(store, result)
    return result
  } catch (e) {
    if (!(e instanceof TypeError)) throw e
    const tempId = -(Date.now())
    const tempRecord = { id: tempId, ...payload, _pending: true }
    if (store) await dbPut(store, tempRecord)
    await offline.enqueue({ method: 'POST', endpoint, payload, store, tempId })
    return tempRecord
  }
}

export async function saveEncryptedOrQueue(endpoint, id, payload, encFields, rawRecord, ks, store) {
  const patched = await buildEncryptedPatch(payload, encFields, rawRecord, ks)
  const offline = useOfflineStore()
  const fullEndpoint = `${endpoint}${id}/`
  try {
    const result = await api.patch(fullEndpoint, patched)
    if (store) await dbPut(store, result)
    return result
  } catch (e) {
    if (!(e instanceof TypeError)) throw e
    const optimistic = { ...(rawRecord ?? {}), ...patched, id: Number(id), _pending: true }
    if (store) await dbPut(store, optimistic)
    await offline.enqueue({ method: 'PATCH', endpoint: fullEndpoint, payload: patched, store })
    return optimistic
  }
}

export async function updateOrQueue(endpoint, id, payload, store, currentIdbRecord) {
  const offline = useOfflineStore()
  const fullEndpoint = `${endpoint}${id}/`
  try {
    const result = await api.patch(fullEndpoint, payload)
    if (store) await dbPut(store, result)
    return result
  } catch (e) {
    if (!(e instanceof TypeError)) throw e
    const optimistic = { ...(currentIdbRecord ?? {}), ...payload, id: Number(id), _pending: true }
    if (store) await dbPut(store, optimistic)
    await offline.enqueue({ method: 'PATCH', endpoint: fullEndpoint, payload, store })
    return optimistic
  }
}

export async function deleteOrQueue(endpoint, id, store) {
  const offline = useOfflineStore()
  const fullEndpoint = `${endpoint}${id}/`
  try {
    await api.delete(fullEndpoint)
    if (store) await dbDelete(store, Number(id))
  } catch (e) {
    if (!(e instanceof TypeError)) throw e
    if (store) await dbDelete(store, Number(id))
    await offline.enqueue({ method: 'DELETE', endpoint: fullEndpoint, store })
  }
}
