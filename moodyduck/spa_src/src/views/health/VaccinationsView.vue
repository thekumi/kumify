<template>
  <div class="pb-nav">
    <TopBar title="Vaccinations" :back="true">
      <template #actions>
        <RouterLink to="/health/vaccinations/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-purple-100 hover:bg-purple-200 transition-colors">
          <i class="ph ph-plus text-purple-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!vaccinations.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-syringe text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No vaccinations recorded</p>
      <RouterLink to="/health/vaccinations/new" class="mt-4 px-5 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-medium hover:bg-purple-700 transition-colors">
        Add vaccination
      </RouterLink>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-for="v in vaccinations" :key="v.id" class="px-4 py-4">
        <div class="flex items-start justify-between">
          <div>
            <p class="font-medium text-stone-800">{{ v.name || '—' }}</p>
            <p v-if="v.target_disease" class="text-xs text-stone-400 mt-0.5">{{ v.target_disease }}</p>
            <p class="text-xs text-stone-500 mt-1">
              Administered: <span class="font-medium">{{ fmtDate(v.administered_on) }}</span>
              <span v-if="v.next_due"> · Next: <span class="font-medium">{{ fmtDate(v.next_due) }}</span></span>
            </p>
          </div>
          <RouterLink :to="`/health/vaccinations/${v.id}/edit`"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0 ml-2">
            <i class="ph ph-pencil-simple text-stone-400"></i>
          </RouterLink>
        </div>
      </li>
    </ul>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getVaccinations } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const vaccinations = ref([])
const raw = ref([])
const loading = ref(true)
const fmtDate = (d) => d ? new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '—'

async function applyDecryption() { vaccinations.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  raw.value = await getVaccinations()
  await applyDecryption()
  loading.value = false
})
</script>
