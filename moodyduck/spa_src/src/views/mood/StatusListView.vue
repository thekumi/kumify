<template>
  <div class="pb-nav">
    <TopBar title="Mood Log">
      <template #actions>
        <RouterLink to="/mood/settings" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
          <i class="ph ph-gear text-stone-500"></i>
        </RouterLink>
        <RouterLink to="/mood/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-clay-100 hover:bg-clay-200 transition-colors">
          <i class="ph ph-plus text-clay-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!statuses.length" class="flex flex-col items-center justify-center py-20 px-6 text-center">
      <i class="ph ph-smiley text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No entries yet</p>
      <p class="text-stone-400 text-sm mt-1">Start tracking how you feel.</p>
      <RouterLink to="/mood/new" class="mt-4 px-5 py-2.5 bg-clay-600 text-white rounded-xl text-sm font-medium hover:bg-clay-700 transition-colors">
        Add entry
      </RouterLink>
    </div>

    <div v-else>
      <ul class="divide-y divide-stone-100 bg-white mx-4 mt-4 rounded-2xl border border-stone-100 shadow-sm overflow-hidden">
        <li v-for="s in statuses" :key="s.id">
          <RouterLink :to="`/mood/${s.id}`" class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
            <div class="w-11 h-11 rounded-full flex items-center justify-center shrink-0"
                 :style="moodFor(s.mood)?.color ? `background:${moodFor(s.mood).color}22` : 'background:#f5f5f4'">
              <i :class="moodFor(s.mood)?.icon || 'ph ph-smiley'"
                 :style="moodFor(s.mood)?.color ? `color:${moodFor(s.mood).color}` : 'color:#a8a29e'"
                 class="text-xl"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-stone-800 leading-snug truncate">
                {{ moodFor(s.mood)?.name || '—' }}
              </p>
              <p class="text-xs text-stone-400 mt-0.5">{{ fmtDate(s.timestamp) }}</p>
              <p v-if="s.title" class="text-xs text-stone-500 truncate mt-0.5">{{ s.title }}</p>
            </div>
            <i class="ph ph-caret-right text-stone-300 shrink-0"></i>
          </RouterLink>
        </li>
      </ul>

      <div v-if="hasMore" class="px-4 py-4">
        <button @click="loadMore" :disabled="loadingMore"
          class="w-full py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors disabled:opacity-50">
          {{ loadingMore ? 'Loading…' : 'Load more' }}
        </button>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getStatuses, getMoods } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const statuses = ref([])
const rawStatuses = ref([])
const moodMap = ref({})
const rawMoods = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)

function moodFor(id) { return moodMap.value[id] ?? null }
function fmtDate(ts) {
  return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function applyDecryption() {
  const [ds, dm] = await Promise.all([
    ks.decryptAll(rawStatuses.value),
    ks.decryptAll(rawMoods.value),
  ])
  statuses.value = ds
  moodMap.value = Object.fromEntries(dm.map(m => [m.id, m]))
}

async function load(p = 1) {
  const [res, moods] = await Promise.all([
    getStatuses(p),
    p === 1 ? getMoods() : Promise.resolve(null),
  ])
  if (moods) rawMoods.value = moods
  rawStatuses.value.push(...(res.results ?? []))
  hasMore.value = !!res.next
  page.value = p
  await applyDecryption()
}

async function loadMore() {
  loadingMore.value = true
  await load(page.value + 1)
  loadingMore.value = false
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  await load()
  loading.value = false
})
</script>
