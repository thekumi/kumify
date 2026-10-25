<template>
    <div v-if="auth.ready" class="min-h-screen bg-clay-50">
        <RouterView />
        <KeystoreOverlay />
        <SyncBanner />
        <PluginPermissionDialog />
        <!-- First-sync overlay: shown while initial data load runs on a fresh device -->
        <Transition name="fade-overlay">
        <div v-if="syncStore.syncing && !syncStore.lastSync"
             class="fixed inset-0 z-30 bg-clay-50/95 backdrop-blur-sm flex flex-col items-center justify-center gap-4">
            <div class="w-10 h-10 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
            <p class="text-stone-500 font-medium text-sm">Loading your data…</p>
        </div>
        </Transition>
    </div>
    <div v-else
         class="min-h-screen bg-clay-50 flex items-center justify-center">
        <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>
</template>
<script setup>
import { watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'
import { useSyncStore } from '@/stores/sync'
import KeystoreOverlay from '@/components/KeystoreOverlay.vue'
import SyncBanner from '@/components/SyncBanner.vue'
import PluginPermissionDialog from '@/components/PluginPermissionDialog.vue'
import { syncAndroidContacts, CONTACTS_ENABLED_KEY } from '@/androidContacts'

const auth = useAuthStore()
const ks = useKeystoreStore()
const offline = useOfflineStore()
const syncStore = useSyncStore()

onMounted(async () => {
  auth.init()
  await offline.load()
  if (navigator.onLine) offline.sync()
  window.addEventListener('online', offline.sync)
})

watch(
  () => auth.user,
  (user) => { if (user) ks.boot() },
  { immediate: true }
)

let contactsSynced = false
watch(
  () => ks.status,
  (status) => {
    if (status === 'ready' && !contactsSynced && window.Android
        && localStorage.getItem(CONTACTS_ENABLED_KEY) === '1') {
      contactsSynced = true
      syncAndroidContacts(ks).catch(() => {})
    }
  }
)
</script>
<style scoped>
.fade-overlay-enter-active, .fade-overlay-leave-active { transition: opacity 0.3s ease; }
.fade-overlay-enter-from, .fade-overlay-leave-to { opacity: 0; }
</style>
