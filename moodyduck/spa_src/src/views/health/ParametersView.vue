<template>
  <div class="pb-nav">
    <TopBar title="Health Parameters" :back="true">
      <template #actions>
        <RouterLink to="/health/parameters/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-green-100 hover:bg-green-200 transition-colors">
          <i class="ph ph-plus text-green-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!params.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-chart-line text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No parameters defined</p>
      <p class="text-stone-400 text-sm mt-1">Add parameters like blood pressure, weight, or heart rate to track in health logs.</p>
      <RouterLink to="/health/parameters/new" class="mt-4 px-5 py-2.5 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition-colors">
        Add parameter
      </RouterLink>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-for="p in params" :key="p.id" class="flex items-center gap-3 px-4 py-4">
        <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shrink-0">
          <i :class="p.icon || 'ph ph-heart'" class="text-green-600 text-xl"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="font-medium text-stone-800 truncate">{{ p.name }}</p>
          <p v-if="p.unit" class="text-xs text-stone-400 mt-0.5">Unit: {{ p.unit }}</p>
        </div>
        <RouterLink :to="`/health/parameters/${p.id}/edit`"
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
          <i class="ph ph-pencil-simple text-stone-400"></i>
        </RouterLink>
      </li>
    </ul>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getParameters } from '@/api/health'

const params = ref([])
const loading = ref(true)

onMounted(async () => {
  params.value = await getParameters()
  loading.value = false
})
</script>
