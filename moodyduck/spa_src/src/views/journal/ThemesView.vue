<template>
  <div class="pb-nav">
    <TopBar title="Dream Themes" :back="true">
      <template #actions>
        <RouterLink to="/journal/dreams/themes/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition-colors">
          <i class="ph ph-plus text-blue-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
    </div>

    <ul v-else class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li v-if="!themes.length" class="px-4 py-8 text-center text-stone-400 text-sm">No themes yet.</li>
      <li v-for="t in themes" :key="t.id" class="flex items-center gap-3 px-4 py-3.5">
        <i :class="t.icon || 'ph ph-tag'"
           :style="t.color ? `color:${t.color}` : ''"
           class="text-2xl shrink-0"></i>
        <p class="flex-1 font-medium text-stone-800 truncate">{{ t.name }}</p>
        <RouterLink :to="`/journal/dreams/themes/${t.id}/edit`"
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
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
import { getThemes } from '@/api/dreams'

const themes = ref([])
const loading = ref(true)

onMounted(async () => {
  themes.value = await getThemes().catch(() => [])
  loading.value = false
})
</script>
