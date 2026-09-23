<template>
  <div class="pb-nav">
    <TopBar title="Media Gallery" :back="true" />

    <!-- Filter bar -->
    <div class="sticky top-0 z-10 bg-white border-b border-stone-100 px-4 py-2.5 flex items-center gap-2 flex-wrap">
      <div class="flex gap-1 bg-stone-100 rounded-xl p-0.5 text-xs font-medium">
        <button v-for="f in ['all','images','files']" :key="f"
          @click="typeFilter = f"
          class="px-3 py-1.5 rounded-lg transition-colors capitalize"
          :class="typeFilter === f ? 'bg-white shadow-sm text-stone-800' : 'text-stone-500'">
          {{ f }}
        </button>
      </div>
      <div class="flex gap-1 bg-stone-100 rounded-xl p-0.5 text-xs font-medium ml-auto">
        <button v-for="s in ['newest','oldest','month']" :key="s"
          @click="sortMode = s"
          class="px-2.5 py-1.5 rounded-lg transition-colors capitalize"
          :class="sortMode === s ? 'bg-white shadow-sm text-stone-800' : 'text-stone-500'">
          {{ s }}
        </button>
      </div>
      <button @click="showPrivate = !showPrivate"
        class="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-xl border transition-colors"
        :class="showPrivate ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-stone-200 text-stone-400'">
        <i :class="showPrivate ? 'ph ph-lock-simple-open' : 'ph ph-lock-simple'" class="text-sm"></i>
        Private
      </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <div class="w-8 h-8 border-4 border-stone-200 border-t-rose-500 rounded-full animate-spin"></div>
      <p class="text-sm text-stone-400">Loading media…</p>
    </div>

    <div v-else-if="!visibleItems.length" class="flex flex-col items-center justify-center py-20 px-6 text-center">
      <i class="ph ph-images text-5xl text-stone-300 mb-3"></i>
      <p class="text-stone-500 font-medium">No media yet</p>
      <p class="text-stone-400 text-sm mt-1">Attach photos or files to your journal entries.</p>
    </div>

    <div v-else class="px-4 py-4 space-y-6">
      <div v-for="group in groupedItems" :key="group.label">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-2">{{ group.label }}</p>

        <!-- Image grid -->
        <div v-if="group.images.length" class="grid grid-cols-3 gap-1.5 mb-2">
          <div v-for="item in group.images" :key="item.attachment.id"
               class="relative aspect-square rounded-xl overflow-hidden bg-stone-100">
            <img v-if="loaded[item.attachment.id]?.blobUrl"
                 :src="loaded[item.attachment.id].blobUrl"
                 class="w-full h-full object-cover cursor-pointer hover:opacity-90 transition-opacity"
                 @click="openLightbox(item)" />
            <div v-else class="w-full h-full flex items-center justify-center">
              <div class="w-4 h-4 border-2 border-stone-300 border-t-stone-500 rounded-full animate-spin"></div>
            </div>
            <RouterLink :to="item.sourceUrl"
              class="absolute bottom-1 left-1 w-5 h-5 bg-black/30 hover:bg-black/50 rounded-full flex items-center justify-center transition-colors">
              <i :class="item.sourceType === 'dream' ? 'ph ph-moon-stars' : 'ph ph-smiley'" class="text-white text-xs"></i>
            </RouterLink>
          </div>
        </div>

        <!-- File list -->
        <div v-if="group.files.length" class="space-y-1">
          <div v-for="item in group.files" :key="item.attachment.id"
               class="flex items-center gap-3 px-3 py-2.5 bg-stone-50 rounded-xl">
            <i class="ph ph-file text-stone-400 text-xl shrink-0"></i>
            <a v-if="loaded[item.attachment.id]?.blobUrl"
               :href="loaded[item.attachment.id].blobUrl"
               :download="loaded[item.attachment.id].name ?? item.attachment.name"
               class="text-sm text-clay-600 hover:underline truncate flex-1">
              {{ loaded[item.attachment.id].name ?? item.attachment.name }}
            </a>
            <span v-else class="text-sm text-stone-400 truncate flex-1">{{ item.attachment.name }}</span>
            <RouterLink :to="item.sourceUrl" class="text-stone-300 hover:text-stone-500 shrink-0">
              <i :class="item.sourceType === 'dream' ? 'ph ph-moon-stars' : 'ph ph-smiley'" class="text-base"></i>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <div v-if="lightbox" class="fixed inset-0 z-50 bg-black/85 flex flex-col items-center justify-center p-4"
           @click="lightbox = null">
        <img :src="loaded[lightbox.attachment.id]?.blobUrl"
             class="max-w-full max-h-[80vh] rounded-lg object-contain"
             @click.stop />
        <RouterLink :to="lightbox.sourceUrl" @click="lightbox = null"
          class="mt-3 text-white/70 hover:text-white text-sm flex items-center gap-1.5">
          <i :class="lightbox.sourceType === 'dream' ? 'ph ph-moon-stars' : 'ph ph-smiley'"></i>
          View source entry
        </RouterLink>
        <button @click="lightbox = null"
          class="absolute top-4 right-4 w-9 h-9 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center">
          <i class="ph ph-x text-white text-lg"></i>
        </button>
      </div>
    </Teleport>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { getAllStatuses } from '@/api/mood'
import { getAllDreams } from '@/api/dreams'
import { b64decode } from '@/keystore/util'

const ks = useKeystoreStore()
const loading = ref(true)
const typeFilter = ref('all')
const sortMode = ref('newest')
const showPrivate = ref(false)
const lightbox = ref(null)

// id -> { blobUrl, mime, private, name }
const loaded = ref({})
const blobsToRevoke = []

// Flat list of { attachment, timestamp, sourceType, sourceId, sourceUrl }
const allItems = ref([])

function getMime(attachment) {
  if (attachment.encrypted_payload?.mime) return attachment.encrypted_payload.mime
  const ext = attachment.name?.split('.').pop()?.toLowerCase() ?? ''
  return { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif',
           webp: 'image/webp', mp4: 'video/mp4', pdf: 'application/pdf' }[ext] ?? 'application/octet-stream'
}

async function loadItem(item) {
  const att = item.attachment
  if (att.id in loaded.value) return
  try {
    const ep = att.encrypted_payload
    if (ep?.v >= 1 && ep.iv) {
      if (!ks.dataKey) return
      let meta = { mime: ep.mime ?? 'application/octet-stream', private: false, name: att.name }
      if (ep.v === 2) {
        const metaBytes = await crypto.subtle.decrypt(
          { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.meta_iv)) },
          ks.dataKey,
          b64decode(ep.meta_ct),
        )
        meta = JSON.parse(new TextDecoder().decode(metaBytes))
      }
      if (!showPrivate.value && meta.private) {
        loaded.value = { ...loaded.value, [att.id]: { blobUrl: null, mime: meta.mime, private: true, name: meta.name ?? att.name } }
        return
      }
      const res = await fetch(att.url)
      const encrypted = await res.arrayBuffer()
      const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.iv)) },
        ks.dataKey,
        encrypted,
      )
      const blob = new Blob([decrypted], { type: meta.mime })
      const blobUrl = URL.createObjectURL(blob)
      blobsToRevoke.push(blobUrl)
      loaded.value = { ...loaded.value, [att.id]: { blobUrl, mime: meta.mime, private: meta.private, name: meta.name ?? att.name } }
    } else if (att.url) {
      loaded.value = { ...loaded.value, [att.id]: { blobUrl: att.url, mime: getMime(att), private: false, name: att.name } }
    }
  } catch (e) {
    console.warn('[gallery] load failed for', att.id, e)
    loaded.value = { ...loaded.value, [att.id]: null }
  }
}

const visibleItems = computed(() => {
  return allItems.value.filter(item => {
    const l = loaded.value[item.attachment.id]
    if (l && l.private && !showPrivate.value) return false
    const mime = l?.mime ?? getMime(item.attachment)
    if (typeFilter.value === 'images' && !mime.startsWith('image/')) return false
    if (typeFilter.value === 'files' && mime.startsWith('image/')) return false
    return true
  })
})

const groupedItems = computed(() => {
  const items = [...visibleItems.value]
  if (sortMode.value === 'oldest') items.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  else items.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  if (sortMode.value !== 'month') {
    const images = items.filter(i => (loaded.value[i.attachment.id]?.mime ?? getMime(i.attachment)).startsWith('image/'))
    const files  = items.filter(i => !(loaded.value[i.attachment.id]?.mime ?? getMime(i.attachment)).startsWith('image/'))
    return [{ label: `${items.length} item${items.length !== 1 ? 's' : ''}`, images, files }]
  }

  const byMonth = {}
  for (const item of items) {
    const label = new Date(item.timestamp).toLocaleString('default', { month: 'long', year: 'numeric' })
    if (!byMonth[label]) byMonth[label] = []
    byMonth[label].push(item)
  }
  return Object.entries(byMonth).map(([label, monthItems]) => ({
    label,
    images: monthItems.filter(i => (loaded.value[i.attachment.id]?.mime ?? getMime(i.attachment)).startsWith('image/')),
    files:  monthItems.filter(i => !(loaded.value[i.attachment.id]?.mime ?? getMime(i.attachment)).startsWith('image/')),
  }))
})

function openLightbox(item) { lightbox.value = item }

async function load() {
  if (!ks.dataKey) return
  loading.value = true
  try {
    const [rawStatuses, rawDreams] = await Promise.all([getAllStatuses(), getAllDreams()])
    const items = []
    for (const s of rawStatuses) {
      for (const att of (s.attachments ?? [])) {
        items.push({ attachment: att, timestamp: s.timestamp, sourceType: 'status', sourceId: s.id, sourceUrl: `/mood/${s.id}` })
      }
    }
    for (const d of rawDreams) {
      for (const att of (d.attachments ?? [])) {
        items.push({ attachment: att, timestamp: d.timestamp, sourceType: 'dream', sourceId: d.id, sourceUrl: `/journal/dreams/${d.id}` })
      }
    }
    allItems.value = items
    for (const item of items) loadItem(item)
  } finally {
    loading.value = false
  }
}

watch(() => ks.dataKey, (k) => { if (k) load() })
watch(showPrivate, () => {
  // Re-evaluate items that were skipped due to privacy filter
  for (const item of allItems.value) {
    const l = loaded.value[item.attachment.id]
    if (l?.private) delete loaded.value[item.attachment.id]
  }
  for (const item of allItems.value) loadItem(item)
})
onMounted(() => { if (ks.dataKey) load() })
onUnmounted(() => { for (const url of blobsToRevoke) URL.revokeObjectURL(url) })
</script>
