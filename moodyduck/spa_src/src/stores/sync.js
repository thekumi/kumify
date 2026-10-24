import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sync as runSync, getLastSync, onSyncComplete, offSyncComplete } from '@/lib/sync'

export const useSyncStore = defineStore('sync', () => {
  const syncing = ref(false)
  const lastSync = ref(null)
  const revision = ref(0)

  async function init() {
    lastSync.value = await getLastSync()
    onSyncComplete(_onComplete)
  }

  function _onComplete() {
    getLastSync().then(ts => { lastSync.value = ts })
    revision.value++
  }

  async function trigger(opts) {
    syncing.value = true
    try {
      await runSync(opts)
    } finally {
      syncing.value = false
    }
  }

  function dispose() {
    offSyncComplete(_onComplete)
  }

  return { syncing, lastSync, revision, init, trigger, dispose }
})
