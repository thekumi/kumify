<template>
    <div class="pb-nav">
        <TopBar title="Medications" :back="true">
        <template #actions>
            <RouterLink to="/health/medications/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition-colors">
            <i class="ph ph-plus text-blue-700"></i>
            </RouterLink>
        </template>
        </TopBar>
        <div v-if="loading" class="flex justify-center py-16">
            <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <div v-else-if="!meds.length"
             class="flex flex-col items-center py-20 text-center px-6">
            <i class="ph ph-pill text-6xl text-stone-300 mb-4"></i>
            <p class="text-stone-500 font-medium">No medications added</p>
            <RouterLink to="/health/medications/new" class="mt-4 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors">
            Add medication
            </RouterLink>
        </div>
        <ul v-else
            class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
            <li v-for="m in meds"
                :key="m.id"
                class="flex items-center gap-3 px-4 py-4">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <i :class="m.icon || 'ph ph-pill'" class="text-blue-600 text-xl"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="font-medium text-stone-800 truncate">{{ m.name || '—' }}</p>
                    <div class="flex items-center gap-2 mt-0.5 flex-wrap">
                        <span v-if="m.prn"
                              class="text-xs px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded-md font-medium">PRN</span>
                        <span v-else-if="scheduleLabel(m)"
                              class="text-xs text-stone-400 truncate">{{ scheduleLabel(m) }}</span>
                        <span v-if="m.dosage" class="text-xs text-stone-400">· {{ m.dosage }}</span>
                    </div>
                </div>
                <RouterLink :to="`/health/medications/${m.id}/edit`" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
                <i class="ph ph-pencil-simple text-stone-400"></i>
                </RouterLink>
            </li>
        </ul>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getMedications } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'

const DAY_NAMES = { MO: 'Mon', TU: 'Tue', WE: 'Wed', TH: 'Thu', FR: 'Fri', SA: 'Sat', SU: 'Sun' }

const ks = useKeystoreStore()
const meds = ref([])
const raw = ref([])
const loading = ref(true)

function scheduleLabel(med) {
  if (!med.rrule && !med.times?.length) return null
  const parts = []
  if (med.rrule) {
    const r = Object.fromEntries(med.rrule.split(';').map(p => p.split('=')))
    const freqMap = { DAILY: 'Daily', WEEKLY: 'Weekly', MONTHLY: 'Monthly', YEARLY: 'Yearly' }
    const freq = freqMap[r.FREQ] || r.FREQ
    const interval = r.INTERVAL > 1 ? ` every ${r.INTERVAL}` : ''
    const days = r.BYDAY
      ? ` on ${r.BYDAY.split(',').map(d => DAY_NAMES[d] || d).join(', ')}`
      : ''
    parts.push(`${freq}${interval}${days}`)
  }
  if (med.times?.length) parts.push(`at ${med.times.join(', ')}`)
  return parts.join(' ') || null
}

async function applyDecryption() { meds.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  raw.value = await getMedications().catch(() => [])
  await applyDecryption()
  loading.value = false
})
</script>
