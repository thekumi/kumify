<template>
  <div class="pb-nav">
    <TopBar title="Activities" :back="true">
      <template #actions>
        <RouterLink to="/mood/settings/activities/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-clay-100 hover:bg-clay-200 transition-colors">
          <i class="ph ph-plus text-clay-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-if="!activities.length" class="px-4 py-8 text-center text-stone-400 text-sm">No activities yet.</li>
      <li v-for="a in activities" :key="a.id" class="flex items-center gap-3 px-4 py-3.5">
        <i :class="a.icon || 'ph ph-check'"
           :style="a.color ? `color:${a.color}` : ''"
           class="text-2xl shrink-0"></i>
        <p class="flex-1 font-medium text-stone-800 truncate">{{ a.name || '—' }}</p>
        <RouterLink :to="`/mood/settings/activities/${a.id}/edit`"
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
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
import { getActivities } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const activities = ref([])
const raw = ref([])
const loading = ref(true)

async function applyDecryption() { activities.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  raw.value = await getActivities()
  await applyDecryption()
  loading.value = false
})
</script>
