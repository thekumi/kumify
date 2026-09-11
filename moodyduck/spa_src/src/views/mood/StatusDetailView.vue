<template>
  <div class="pb-nav">
    <TopBar :title="mood?.name || 'Entry'" :back="true">
      <template #actions>
        <RouterLink :to="`/mood/${id}/edit`" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
          <i class="ph ph-pencil-simple text-stone-600"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="status" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5 flex items-center gap-4">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center shrink-0"
             :style="mood?.color ? `background:${mood.color}22` : 'background:#f5f5f4'">
          <i :class="mood?.icon ? `ph ${mood.icon}` : 'ph ph-smiley'"
             :style="mood?.color ? `color:${mood.color}` : 'color:#a8a29e'"
             class="text-4xl"></i>
        </div>
        <div>
          <p class="text-xl font-bold text-stone-800">{{ mood?.name || '—' }}</p>
          <p class="text-sm text-stone-400 mt-0.5">{{ fmtDate(status.timestamp) }}</p>
        </div>
      </div>

      <div v-if="status.title || status.text" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
        <h2 v-if="status.title" class="font-semibold text-stone-800 mb-2">{{ status.title }}</h2>
        <p v-if="status.text" class="text-stone-600 text-sm whitespace-pre-wrap leading-relaxed">{{ status.text }}</p>
      </div>

      <div v-if="status.activities?.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-3">Activities</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="a in decryptedActivities" :key="a.id"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-stone-100 text-stone-700 text-sm font-medium">
            <i :class="a.icon ? `ph ${a.icon}` : 'ph ph-check'" :style="a.color ? `color:${a.color}` : ''" class="text-base"></i>
            {{ a.name || '—' }}
          </span>
        </div>
      </div>

      <button @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors mt-2">
        Delete entry
      </button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getStatus, deleteStatus, getMoods } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const status = ref(null)
const rawMoods = ref([])
const decryptedMoods = ref([])
const decryptedActivities = ref([])
const loading = ref(true)

const mood = computed(() => decryptedMoods.value.find(m => m.id === status.value?.mood) ?? null)

function fmtDate(ts) {
  return new Date(ts).toLocaleString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function applyDecryption() {
  if (!status.value) return
  const [ds, dm, da] = await Promise.all([
    ks.decrypt(status.value),
    ks.decryptAll(rawMoods.value),
    ks.decryptAll(status.value.activities ?? []),
  ])
  status.value = ds
  decryptedMoods.value = dm
  decryptedActivities.value = da
}

async function remove() {
  if (!confirm('Delete this entry?')) return
  await deleteStatus(id)
  router.push('/mood')
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  const [s, m] = await Promise.all([getStatus(id), getMoods()])
  status.value = s
  rawMoods.value = m
  await applyDecryption()
  loading.value = false
})
</script>
