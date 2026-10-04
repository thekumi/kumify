<template>
  <div class="pb-nav">
    <TopBar title="Activities" :back="true">
      <template #actions>
        <RouterLink to="/mood/settings/activities/new"
          class="w-8 h-8 flex items-center justify-center rounded-full bg-clay-100 hover:bg-clay-200 transition-colors">
          <i class="ph ph-plus text-clay-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <div v-else class="px-4 mt-4 space-y-4">
      <!-- Manage categories link -->
      <RouterLink to="/mood/settings/activities/categories"
        class="flex items-center gap-2 text-sm text-clay-600 font-medium px-1">
        <i class="ph ph-tag text-base"></i>
        Manage categories
        <i class="ph ph-caret-right text-xs ml-auto text-stone-300"></i>
      </RouterLink>

      <div v-if="!activities.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm px-4 py-8 text-center text-stone-400 text-sm">
        No activities yet.
      </div>

      <!-- Grouped by category -->
      <template v-for="group in grouped" :key="group.id ?? 'uncategorized'">
        <div>
          <div v-if="group.label" class="flex items-center gap-2 mb-1.5 px-1">
            <i :class="group.icon || 'ph ph-tag'" :style="group.color ? `color:${group.color}` : ''" class="text-base shrink-0"></i>
            <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">{{ group.label }}</p>
          </div>
          <ul class="bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
            <li v-for="a in group.items" :key="a.id" class="flex items-center gap-3 px-4 py-3.5">
              <i :class="a.icon || 'ph ph-check'" :style="a.color ? `color:${a.color}` : ''" class="text-2xl shrink-0"></i>
              <p class="flex-1 font-medium text-stone-800 truncate">{{ a.name || '—' }}</p>
              <RouterLink :to="`/mood/settings/activities/${a.id}/edit`"
                class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
                <i class="ph ph-pencil-simple text-stone-400"></i>
              </RouterLink>
            </li>
          </ul>
        </div>
      </template>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getActivities, getActivityCategories } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const activities = ref([])
const raw = ref([])
const categories = ref([])
const rawCategories = ref([])
const loading = ref(true)

async function applyDecryption() {
  activities.value = await ks.decryptAll(raw.value)
  categories.value = await ks.decryptAll(rawCategories.value)
}
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

const grouped = computed(() => {
  const catMap = Object.fromEntries(categories.value.map(c => [c.id, c]))
  const groups = {}

  for (const a of activities.value) {
    const key = a.category ?? 'none'
    if (!groups[key]) {
      const cat = a.category ? catMap[a.category] : null
      groups[key] = {
        id: a.category ?? null,
        label: cat?.name ?? (a.category ? null : null),
        icon: cat?.icon,
        color: cat?.color,
        items: [],
      }
    }
    groups[key].items.push(a)
  }

  // Sort: categorized groups first (alphabetically), then uncategorized
  return Object.values(groups).sort((a, b) => {
    if (a.id === null && b.id !== null) return 1
    if (a.id !== null && b.id === null) return -1
    return (a.label ?? '').localeCompare(b.label ?? '')
  })
})

onMounted(async () => {
  ;[raw.value, rawCategories.value] = await Promise.all([getActivities(), getActivityCategories()])
  await applyDecryption()
  loading.value = false
})
</script>
