<template>
  <div class="pb-nav">
    <TopBar title="Thought Records" :back="true">
      <template #actions>
        <RouterLink to="/journal/cbt/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-purple-100 hover:bg-purple-200 transition-colors">
          <i class="ph ph-plus text-purple-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!records.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-brain text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No thought records yet</p>
      <RouterLink to="/journal/cbt/new" class="mt-4 px-5 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-medium hover:bg-purple-700 transition-colors">
        New thought record
      </RouterLink>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-for="r in records" :key="r.id">
        <RouterLink :to="`/journal/cbt/${r.id}`" class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
          <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center shrink-0">
            <i class="ph ph-brain text-purple-600 text-xl"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-stone-800 truncate">{{ r.title || 'Untitled' }}</p>
            <p v-if="r.situation" class="text-xs text-stone-400 truncate mt-0.5">{{ r.situation }}</p>
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

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getRecords } from '@/api/cbt'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const records = ref([])
const rawRecords = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)

async function applyDecryption() { records.value = await ks.decryptAll(rawRecords.value) }

async function load(p = 1) {
  const res = await getRecords(p)
  rawRecords.value.push(...(res.results ?? []))
  hasMore.value = !!res.next
  page.value = p
  await applyDecryption()
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })
async function loadMore() { loadingMore.value = true; await load(page.value + 1); loadingMore.value = false }
onMounted(async () => { await load(); loading.value = false })
</script>
