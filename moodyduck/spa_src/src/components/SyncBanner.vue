<template>
  <Transition name="slide-up">
    <div v-if="offline.count > 0 || offline.syncing"
      class="fixed bottom-16 inset-x-0 z-40 flex justify-center pointer-events-none px-4 pb-2">
      <div class="bg-stone-800/90 backdrop-blur-sm text-white text-sm font-medium px-4 py-2 rounded-full shadow-lg flex items-center gap-2">
        <div v-if="offline.syncing" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0"></div>
        <i v-else class="ph ph-cloud-arrow-up text-base shrink-0"></i>
        <span v-if="offline.syncing">Syncing…</span>
        <span v-else>{{ offline.count }} {{ offline.count === 1 ? 'entry' : 'entries' }} pending sync</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useOfflineStore } from '@/stores/offline'
const offline = useOfflineStore()
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.25s ease, opacity 0.25s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(6px); opacity: 0; }
</style>
