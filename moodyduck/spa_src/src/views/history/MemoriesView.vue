<template>
  <div class="pb-nav">
    <TopBar title="Memories" :back="true" />

    <!-- Date picker + milestones -->
    <div class="px-4 pt-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <label class="text-sm font-semibold text-stone-500 block mb-2">Browse a date</label>
        <input type="date" v-model="selectedDate"
          class="w-full text-stone-800 text-sm border border-stone-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-400" />
      </div>

      <div class="flex flex-wrap gap-2">
        <button v-for="m in milestones" :key="m.label"
          @click="selectedDate = m.date"
          class="text-xs px-3 py-1.5 rounded-full border font-medium transition-colors"
          :class="selectedDate === m.date ? 'border-amber-400 bg-amber-50 text-amber-700' : 'border-stone-200 text-stone-500 hover:border-stone-300'">
          {{ m.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-7 h-7 border-4 border-stone-200 border-t-amber-500 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!dataLoaded" class="flex flex-col items-center justify-center py-16 px-6 text-center">
      <i class="ph ph-shooting-star text-5xl text-stone-300 mb-3"></i>
      <p class="text-stone-400 text-sm">Loading your memories…</p>
    </div>

    <div v-else-if="!memories.length" class="flex flex-col items-center justify-center py-16 px-6 text-center">
      <i class="ph ph-calendar-blank text-5xl text-stone-300 mb-3"></i>
      <p class="text-stone-500 font-medium">Nothing on this day</p>
      <p class="text-stone-400 text-sm mt-1">{{ formattedDate }}</p>
    </div>

    <div v-else class="px-4 py-4 space-y-3">
      <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">{{ formattedDate }}</p>

      <div v-for="entry in memories" :key="entry.id"
           class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden">
        <RouterLink :to="entry.url" class="block">
          <!-- First photo thumbnail if available -->
          <div v-if="entry.thumbUrl" class="w-full aspect-video bg-stone-100 overflow-hidden">
            <img :src="entry.thumbUrl" class="w-full h-full object-cover" />
          </div>

          <div class="p-4 flex items-start gap-3">
            <!-- Mood icon -->
            <div v-if="entry.mood" class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                 :style="entry.mood.color ? `background:${entry.mood.color}22` : 'background:#f5f5f4'">
              <i :class="entry.mood.icon || 'ph ph-smiley'"
                 :style="entry.mood.color ? `color:${entry.mood.color}` : 'color:#a8a29e'"
                 class="text-2xl"></i>
            </div>
            <div v-else class="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center shrink-0">
              <i :class="entry.type === 'dream' ? 'ph ph-moon-stars text-blue-500' : 'ph ph-note-pencil text-stone-400'" class="text-xl"></i>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span v-if="entry.mood" class="text-sm font-semibold text-stone-800">{{ entry.mood.name }}</span>
                <span v-else class="text-sm font-semibold text-stone-800">{{ entry.type === 'dream' ? 'Dream' : 'Entry' }}</span>
                <span class="text-xs text-stone-400">{{ entry.timeStr }}</span>
              </div>
              <p v-if="entry.title" class="text-sm font-medium text-stone-700 mt-0.5">{{ entry.title }}</p>
              <p v-if="entry.text" class="text-sm text-stone-500 mt-0.5 line-clamp-3 leading-relaxed">{{ entry.text }}</p>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { getAllStatuses, getMoods } from '@/api/mood'
import { getAllDreams } from '@/api/dreams'
import { b64decode } from '@/keystore/util'

const ks = useKeystoreStore()
const loading = ref(false)
const dataLoaded = ref(false)
const selectedDate = ref(todayStr())
const blobsToRevoke = []

const allStatuses = ref([])
const allDreams = ref([])
const moodMap = ref({})

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

const milestones = computed(() => {
  const base = selectedDate.value ? new Date(selectedDate.value + 'T12:00:00') : new Date()
  return [
    { label: '1 month ago',  date: offset(base, 0, -1, 0) },
    { label: '3 months ago', date: offset(base, 0, -3, 0) },
    { label: '6 months ago', date: offset(base, 0, -6, 0) },
    { label: '1 year ago',   date: offset(base, -1, 0, 0) },
    { label: '2 years ago',  date: offset(base, -2, 0, 0) },
    { label: '3 years ago',  date: offset(base, -3, 0, 0) },
    { label: '5 years ago',  date: offset(base, -5, 0, 0) },
  ].filter(m => m.date < todayStr())
})

function offset(base, years, months, days) {
  const d = new Date(base)
  d.setFullYear(d.getFullYear() + years)
  d.setMonth(d.getMonth() + months)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

const formattedDate = computed(() => {
  if (!selectedDate.value) return ''
  return new Date(selectedDate.value + 'T12:00:00').toLocaleDateString(undefined, {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
})

function moodFor(entry) {
  const mid = entry.mood_id != null ? Number(entry.mood_id) : (entry.mood != null ? Number(entry.mood) : null)
  return mid != null ? moodMap.value[mid] ?? null : null
}

const memories = computed(() => {
  if (!selectedDate.value || !dataLoaded.value) return []
  const results = []

  for (const s of allStatuses.value) {
    if (s.timestamp?.slice(0, 10) !== selectedDate.value) continue
    results.push({
      id: `status-${s.id}`,
      type: 'status',
      url: `/mood/${s.id}`,
      mood: moodFor(s),
      title: s.title ?? null,
      text: s.text ?? null,
      timeStr: new Date(s.timestamp).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }),
      firstAttachment: (s.attachments ?? [])[0] ?? null,
      thumbUrl: null,
    })
  }

  for (const d of allDreams.value) {
    if (d.timestamp?.slice(0, 10) !== selectedDate.value) continue
    results.push({
      id: `dream-${d.id}`,
      type: 'dream',
      url: `/journal/dreams/${d.id}`,
      mood: moodFor(d),
      title: d.title ?? null,
      text: d.content ?? null,
      timeStr: new Date(d.timestamp).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }),
      firstAttachment: (d.attachments ?? [])[0] ?? null,
      thumbUrl: null,
    })
  }

  results.sort((a, b) => a.timeStr.localeCompare(b.timeStr))
  return results
})

// Decrypt first-attachment thumbnails reactively
watch(memories, async (entries) => {
  for (const entry of entries) {
    if (!entry.firstAttachment || entry.thumbUrl) continue
    const att = entry.firstAttachment
    const ep = att.encrypted_payload
    if (!ep?.iv || !ks.dataKey) continue
    try {
      let mime = ep.mime ?? 'application/octet-stream'
      if (ep.v === 2) {
        const metaBytes = await crypto.subtle.decrypt(
          { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.meta_iv)) },
          ks.dataKey, b64decode(ep.meta_ct),
        )
        const meta = JSON.parse(new TextDecoder().decode(metaBytes))
        if (meta.private) continue
        mime = meta.mime
      }
      if (!mime.startsWith('image/')) continue
      const res = await fetch(att.url)
      const encrypted = await res.arrayBuffer()
      const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: new Uint8Array(b64decode(ep.iv)) },
        ks.dataKey, encrypted,
      )
      const blobUrl = URL.createObjectURL(new Blob([decrypted], { type: mime }))
      blobsToRevoke.push(blobUrl)
      entry.thumbUrl = blobUrl
    } catch (e) {
      console.warn('[memories] thumb load failed', att.id, e)
    }
  }
}, { deep: false })

async function load() {
  if (!ks.dataKey) return
  loading.value = true
  try {
    const [rawStatuses, rawMoods, rawDreams] = await Promise.all([
      getAllStatuses(), getMoods(), getAllDreams(),
    ])
    const [statuses, moods, dreams] = await Promise.all([
      ks.decryptAll(rawStatuses), ks.decryptAll(rawMoods), ks.decryptAll(rawDreams),
    ])
    allStatuses.value = statuses
    allDreams.value = dreams
    moodMap.value = Object.fromEntries(moods.map(m => [m.id, m]))
    dataLoaded.value = true
  } finally {
    loading.value = false
  }
}

watch(() => ks.dataKey, (k) => { if (k) load() })
onMounted(() => { if (ks.dataKey) load() })
onUnmounted(() => { for (const url of blobsToRevoke) URL.revokeObjectURL(url) })
</script>
