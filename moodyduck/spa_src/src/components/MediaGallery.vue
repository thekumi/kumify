<template>
  <div v-if="attachments.length" class="space-y-2">
    <div v-if="imageItems.length" class="grid grid-cols-3 gap-1.5">
      <div
        v-for="item in imageItems" :key="item.id"
        class="relative aspect-square rounded-xl overflow-hidden bg-stone-100"
      >
        <img
          v-if="loaded[item.id]"
          :src="loaded[item.id].blobUrl"
          class="w-full h-full object-cover cursor-pointer hover:opacity-90 transition-opacity"
          @click="lightbox = item"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <div class="w-5 h-5 border-2 border-stone-300 border-t-stone-500 rounded-full animate-spin"></div>
        </div>
        <button
          v-if="canDelete"
          type="button"
          @click.stop="emit('delete', item.id)"
          class="absolute top-1 right-1 w-5 h-5 bg-black/40 hover:bg-red-500 rounded-full flex items-center justify-center transition-colors"
        >
          <i class="ph ph-x text-white text-xs"></i>
        </button>
      </div>
    </div>

    <div v-if="otherItems.length" class="space-y-1">
      <div
        v-for="item in otherItems" :key="item.id"
        class="flex items-center gap-3 px-3 py-2.5 bg-stone-50 rounded-xl"
      >
        <i class="ph ph-file text-stone-400 text-xl shrink-0"></i>
        <a
          v-if="loaded[item.id]"
          :href="loaded[item.id].blobUrl"
          :download="loaded[item.id].name ?? item.name"
          class="text-sm text-clay-600 hover:underline truncate flex-1"
        >{{ loaded[item.id].name ?? item.name }}</a>
        <span v-else class="text-sm text-stone-400 truncate flex-1">{{ item.name }}</span>
        <button
          v-if="canDelete"
          type="button"
          @click="emit('delete', item.id)"
          class="text-stone-400 hover:text-red-500 transition-colors shrink-0"
        >
          <i class="ph ph-x text-sm"></i>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="lightbox"
        class="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4"
        @click="lightbox = null"
      >
        <img
          :src="loaded[lightbox.id]?.blobUrl"
          class="max-w-full max-h-full rounded-lg object-contain"
          @click.stop
        />
        <button
          @click="lightbox = null"
          class="absolute top-4 right-4 w-9 h-9 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center"
        >
          <i class="ph ph-x text-white text-lg"></i>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { b64decode } from '@/keystore/util'

const props = defineProps({
  attachments: { type: Array, default: () => [] },
  dataKey: { default: null },
  canDelete: { type: Boolean, default: false },
  // When false, items with private: true in their decrypted metadata are hidden.
  showPrivate: { type: Boolean, default: true },
})
const emit = defineEmits(['delete'])

// id -> { blobUrl, mime, private }
const loaded = ref({})
const lightbox = ref(null)
const blobsToRevoke = []

async function decryptMeta(ep, dataKey) {
  if (ep.v === 2) {
    const metaBytes = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.meta_iv)) },
      dataKey,
      b64decode(ep.meta_ct),
    )
    return JSON.parse(new TextDecoder().decode(metaBytes))
  }
  // v1: mime is plaintext, no private flag
  return { mime: ep.mime ?? 'application/octet-stream', private: false }
}

function guessMime(name) {
  const ext = name?.split('.').pop()?.toLowerCase() ?? ''
  return { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif',
           webp: 'image/webp', mp4: 'video/mp4', mov: 'video/quicktime',
           pdf: 'application/pdf' }[ext] ?? 'application/octet-stream'
}

async function loadItem(item) {
  if (item.id in loaded.value) return
  try {
    const ep = item.encrypted_payload
    if (ep?.v >= 1 && ep.iv) {
      if (!props.dataKey) return
      const meta = await decryptMeta(ep, props.dataKey)
      // Fetch and decrypt the file only after we know it should be visible.
      if (!props.showPrivate && meta.private) {
        loaded.value = { ...loaded.value, [item.id]: { blobUrl: null, mime: meta.mime, private: true } }
        return
      }
      const res = await fetch(item.url)
      const encrypted = await res.arrayBuffer()
      const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.iv)) },
        props.dataKey,
        encrypted,
      )
      const blob = new Blob([decrypted], { type: meta.mime })
      const blobUrl = URL.createObjectURL(blob)
      blobsToRevoke.push(blobUrl)
      loaded.value = { ...loaded.value, [item.id]: { blobUrl, mime: meta.mime, private: meta.private, name: meta.name ?? item.name } }
    } else if (item.url) {
      loaded.value = { ...loaded.value, [item.id]: { blobUrl: item.url, mime: guessMime(item.name), private: false } }
    }
  } catch (e) {
    console.warn('[gallery] load failed for', item.id, e)
    loaded.value = { ...loaded.value, [item.id]: null }
  }
}

const visible = computed(() =>
  props.attachments.filter(a => {
    const l = loaded.value[a.id]
    if (!l) return true  // not yet loaded — show placeholder
    return props.showPrivate || !l.private
  })
)
const imageItems = computed(() => visible.value.filter(a => (loaded.value[a.id]?.mime ?? guessMime(a.name)).startsWith('image/')))
const otherItems = computed(() => visible.value.filter(a => !(loaded.value[a.id]?.mime ?? guessMime(a.name)).startsWith('image/')))

watch(
  [() => props.attachments, () => props.dataKey],
  async () => {
    for (const item of props.attachments) await loadItem(item)
  },
  { immediate: true },
)

onUnmounted(() => { for (const url of blobsToRevoke) URL.revokeObjectURL(url) })
</script>
