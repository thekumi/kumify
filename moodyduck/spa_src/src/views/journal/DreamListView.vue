<template>
    <div class="pb-nav">
        <TopBar title="Dreams" :back="true">
        <template #actions>
            <RouterLink to="/journal/dreams/themes" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
            <i class="ph ph-tag text-stone-500"></i>
            </RouterLink>
            <RouterLink to="/journal/dreams/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition-colors">
            <i class="ph ph-plus text-blue-700"></i>
            </RouterLink>
        </template>
        </TopBar>
        <div v-if="loading" class="flex justify-center py-16">
            <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <div v-else-if="!paged.length"
             class="flex flex-col items-center py-20 text-center px-6">
            <i class="ph ph-moon-stars text-6xl text-stone-300 mb-4"></i>
            <p class="text-stone-500 font-medium">No dreams recorded</p>
            <RouterLink to="/journal/dreams/new" class="mt-4 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors">
            Record a dream
            </RouterLink>
        </div>
        <ul v-else
            class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
            <li v-for="d in paged" :key="d.id">
                <RouterLink :to="`/journal/dreams/${d.id}`" class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <i class="ph ph-moon-stars text-blue-600 text-xl"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-stone-800 truncate">{{ d.title || 'Untitled dream' }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">{{ fmtDate(d.timestamp) }} · {{ typeLabel(d.type) }}</p>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                    <span v-if="d.lucid"
                          class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">Lucid</span>
                    <i class="ph ph-caret-right text-stone-300"></i>
                </div>
                </RouterLink>
            </li>
        </ul>
        <div v-if="hasMore" class="px-4 py-4">
            <button type="button"
                    @click="visibleCount += PAGE_SIZE"
                    class="w-full py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">
                Load more
            </button>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { dbGetAll } from '@/lib/db'
import { useKeystoreStore } from '@/stores/keystore'
import { useSyncStore } from '@/stores/sync'

const ks = useKeystoreStore()
const syncStore = useSyncStore()
const types = { 0: 'Night sleep', 1: 'Daydream', 2: 'Nap' }
const typeLabel = (t) => types[t] ?? 'Dream'
const fmtDate = (ts) => new Date(ts).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })

const PAGE_SIZE = 20
const visibleCount = ref(PAGE_SIZE)
const rawDreams = ref([])
const dreams = ref([])
const loading = ref(true)

const paged = computed(() => dreams.value.slice(0, visibleCount.value))
const hasMore = computed(() => dreams.value.length > visibleCount.value)

async function loadFromDB() {
  const raw = await dbGetAll('dreams')
  rawDreams.value = raw.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  dreams.value = await ks.decryptAll(rawDreams.value)
}

watch(() => ks.dataKey, key => { if (key) loadFromDB() })
watch(() => syncStore.revision, () => loadFromDB())
onMounted(async () => { await loadFromDB().catch(() => {}); loading.value = false })
</script>
