<template>
  <div class="pb-nav">
    <TopBar :title="dream?.title || 'Dream'" :back="true">
      <template #actions>
        <RouterLink :to="`/journal/dreams/${id}/edit`" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
          <i class="ph ph-pencil-simple text-stone-600"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="dream" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center">
            <i class="ph ph-moon-stars text-blue-600 text-2xl"></i>
          </div>
          <div>
            <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">{{ typeLabel(dream.type) }}</p>
            <p class="text-sm text-stone-500">{{ fmtDate(dream.timestamp) }}</p>
          </div>
        </div>
        <div class="flex gap-2 flex-wrap">
          <span v-if="dream.lucid" class="text-xs px-2.5 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">Lucid</span>
          <span v-if="dream.wet" class="text-xs px-2.5 py-1 bg-pink-100 text-pink-700 rounded-full font-medium">Wet dream</span>
          <span v-if="mood" class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 bg-stone-50 rounded-full font-medium border border-stone-100">
            <i :class="mood.icon || 'ph ph-smiley'" :style="mood.color ? `color:${mood.color}` : ''" class="text-base"></i>
            {{ mood.name }}
          </span>
        </div>
        <div v-if="dream.themes?.length" class="flex gap-2 flex-wrap mt-2">
          <span v-for="t in dream.themes" :key="t.id"
            class="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-stone-50 rounded-full border border-stone-100 text-stone-600">
            <i :class="t.icon || 'ph ph-tag'" :style="t.color ? `color:${t.color}` : ''" class="text-base"></i>
            {{ t.name }}
          </span>
        </div>
      </div>

      <div v-if="dream.title || dream.content" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
        <h2 v-if="dream.title" class="font-semibold text-stone-800 mb-2">{{ dream.title }}</h2>
        <p v-if="dream.content" class="text-stone-600 text-sm whitespace-pre-wrap leading-relaxed">{{ dream.content }}</p>
      </div>

      <button @click="remove" class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete dream
      </button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getDream, deleteDream } from '@/api/dreams'
import { getMoods } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const dream = ref(null)
const raw = ref(null)
const rawMoods = ref([])
const moodMap = ref({})
const loading = ref(true)

const mood = computed(() => dream.value?.mood != null ? moodMap.value[dream.value.mood] ?? null : null)

const types = { 0: 'Night sleep', 1: 'Daydream', 2: 'Nap' }
const typeLabel = (t) => types[t] ?? 'Dream'
const fmtDate = (ts) => new Date(ts).toLocaleString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })

async function applyDecryption() {
  if (raw.value) dream.value = await ks.decrypt(raw.value)
  const dm = await ks.decryptAll(rawMoods.value)
  moodMap.value = Object.fromEntries(dm.map(m => [m.id, m]))
}

async function remove() {
  if (!confirm('Delete this dream?')) return
  await deleteDream(id)
  router.push('/journal/dreams')
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })
onMounted(async () => {
  const [d, m] = await Promise.all([getDream(id), getMoods().catch(() => [])])
  raw.value = d
  rawMoods.value = m
  await applyDecryption()
  loading.value = false
})
</script>
