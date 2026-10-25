<template>
    <div class="fixed bottom-16 inset-x-0 z-40 flex flex-col items-center gap-1 pb-1.5 px-4 pointer-events-none">
        <!-- App update available -->
        <Transition name="fade">
        <button v-if="updateAvailable"
                type="button"
                @click.stop="applyUpdate"
                class="pointer-events-auto bg-sky-600/95 backdrop-blur-sm text-white text-xs font-medium px-3.5 py-1.5 rounded-full shadow flex items-center gap-2">
            <i class="ph ph-arrow-circle-up text-sm shrink-0"></i>
            <span>Update available</span>
            <span class="opacity-70">· Tap to reload</span>
        </button>
        </Transition>
        <!-- Active states: download sync or upload sync (pills, pointer-events-none) -->
        <Transition name="fade">
        <div v-if="(sync.syncing && sync.lastSync) || upload.syncing"
             class="bg-stone-800/90 backdrop-blur-sm text-white text-xs font-medium px-3.5 py-1.5 rounded-full shadow flex items-center gap-2">
            <div class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0"></div>
            <span>{{ upload.syncing ? 'Uploading…' : 'Syncing…' }}</span>
        </div>
        </Transition>
        <!-- Upload queue: items pending but not yet uploading (tappable pill) -->
        <Transition name="fade">
        <button v-if="upload.count > 0 && !upload.syncing && !(sync.syncing && sync.lastSync)"
                type="button"
                @click.stop="triggerUpload"
                class="pointer-events-auto bg-amber-600/95 backdrop-blur-sm text-white text-xs font-medium px-3.5 py-1.5 rounded-full shadow flex items-center gap-2">
            <i class="ph ph-cloud-arrow-up text-sm shrink-0"></i>
            <span>{{ upload.count }} {{ upload.count === 1 ? 'change' : 'changes' }} pending</span>
            <span class="opacity-70">· Upload now</span>
        </button>
        </Transition>
        <!-- Idle strip: last sync time + manual trigger (always shows after first sync) -->
        <Transition name="fade">
        <button v-if="sync.lastSync && !sync.syncing && !upload.count && !upload.syncing"
                type="button"
                @click.stop="triggerSync"
                class="pointer-events-auto flex items-center gap-1.5 text-stone-400 text-xs px-2 py-1">
            <i class="ph ph-cloud-check text-sm shrink-0"></i>
            <span>{{ relativeTime }}</span>
            <i class="ph ph-arrow-clockwise text-sm shrink-0 opacity-60"></i>
        </button>
        </Transition>
    </div>
</template>
<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useOfflineStore } from '@/stores/offline'
import { useSyncStore } from '@/stores/sync'
import { updateAvailable, applyUpdate } from '@/lib/swUpdate'

const upload = useOfflineStore()
const sync = useSyncStore()

const now = ref(Date.now())
let ticker = null
onMounted(() => { ticker = setInterval(() => { now.value = Date.now() }, 30_000) })
onUnmounted(() => clearInterval(ticker))

const relativeTime = computed(() => {
  if (!sync.lastSync) return ''
  const diff = Math.floor((now.value - new Date(sync.lastSync).getTime()) / 1000)
  if (diff < 60) return 'synced just now'
  if (diff < 3600) return `synced ${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `synced ${Math.floor(diff / 3600)}h ago`
  return `synced ${Math.floor(diff / 86400)}d ago`
})

async function triggerSync() {
  await sync.trigger()
}

async function triggerUpload() {
  await upload.sync()
}
</script>
<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(4px); }
</style>
