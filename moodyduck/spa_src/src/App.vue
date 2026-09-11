<template>
  <div v-if="auth.ready" class="min-h-screen bg-clay-50">
    <RouterView />
    <KeystoreOverlay />
    <SyncBanner />
  </div>
  <div v-else class="min-h-screen bg-clay-50 flex items-center justify-center">
    <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
  </div>
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'
import KeystoreOverlay from '@/components/KeystoreOverlay.vue'
import SyncBanner from '@/components/SyncBanner.vue'

const auth = useAuthStore()
const ks = useKeystoreStore()
const offline = useOfflineStore()

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
</script>
