<template>
  <div class="pb-nav">
    <TopBar title="Activity Categories" :back="true">
      <template #actions>
        <RouterLink to="/mood/settings/activities/categories/new"
          class="w-8 h-8 flex items-center justify-center rounded-full bg-clay-100 hover:bg-clay-200 transition-colors">
          <i class="ph ph-plus text-clay-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-if="!categories.length" class="px-4 py-8 text-center text-stone-400 text-sm">No categories yet.</li>
      <li v-for="c in categories" :key="c.id" class="flex items-center gap-3 px-4 py-3.5">
        <i :class="c.icon || 'ph ph-tag'" :style="c.color ? `color:${c.color}` : ''" class="text-2xl shrink-0"></i>
        <p class="flex-1 font-medium text-stone-800 truncate">{{ c.name || '—' }}</p>
        <RouterLink :to="`/mood/settings/activities/categories/${c.id}/edit`"
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
import { getActivityCategories } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const categories = ref([])
const raw = ref([])
const loading = ref(true)

async function applyDecryption() { categories.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  raw.value = await getActivityCategories()
  await applyDecryption()
  loading.value = false
})
</script>
