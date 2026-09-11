<template>
  <div class="pb-nav">
    <TopBar title="Health Logs" :back="true">
      <template #actions>
        <RouterLink to="/health/logs/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-green-100 hover:bg-green-200 transition-colors">
          <i class="ph ph-plus text-green-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!logs.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-heartbeat text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No health logs yet</p>
      <RouterLink to="/health/logs/new" class="mt-4 px-5 py-2.5 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition-colors">
        Add log
      </RouterLink>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-for="l in logs" :key="l.id" class="px-4 py-4">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-semibold text-stone-800">{{ fmtDate(l.recorded_at) }}</p>
            <p v-if="l.notes" class="text-xs text-stone-400 mt-0.5 truncate">{{ l.notes }}</p>
          </div>
          <RouterLink :to="`/health/logs/${l.id}/edit`" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
            <i class="ph ph-pencil-simple text-stone-400"></i>
          </RouterLink>
        </div>
        <div v-if="l.records?.length" class="flex flex-wrap gap-2 mt-2">
          <span v-for="r in l.records" :key="r.id"
            class="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-green-50 text-green-700 rounded-full font-medium">
            <i class="ph ph-chart-line text-xs"></i>
            {{ r.parameter?.name }}: {{ r.value }} {{ r.parameter?.unit }}
          </span>
        </div>
      </li>
    </ul>

    <div v-if="hasMore" class="px-4 py-4">
      <button @click="loadMore" :disabled="loadingMore"
        class="w-full py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors disabled:opacity-50">
        {{ loadingMore ? 'Loading…' : 'Load more' }}
      </button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getLogs } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const logs = ref([])
const rawLogs = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)

const fmtDate = (ts) => new Date(ts).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })

async function applyDecryption() { logs.value = await ks.decryptAll(rawLogs.value) }

async function load(p = 1) {
  const res = await getLogs(p)
  rawLogs.value.push(...(res.results ?? []))
  hasMore.value = !!res.next
  page.value = p
  await applyDecryption()
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })
async function loadMore() { loadingMore.value = true; await load(page.value + 1); loadingMore.value = false }
onMounted(async () => { await load(); loading.value = false })
</script>
