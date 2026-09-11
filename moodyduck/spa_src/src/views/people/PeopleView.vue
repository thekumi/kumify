<template>
  <div class="pb-nav">
    <TopBar title="People">
      <template #actions>
        <RouterLink to="/people/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-violet-100 hover:bg-violet-200 transition-colors">
          <i class="ph ph-plus text-violet-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!people.length" class="flex flex-col items-center justify-center py-20 px-6 text-center">
      <i class="ph ph-users text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No people yet</p>
      <RouterLink to="/people/new" class="mt-4 px-5 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-medium hover:bg-violet-700 transition-colors">
        Add person
      </RouterLink>
    </div>

    <div v-else class="px-4 mt-4 space-y-2">
      <!-- Emergency contacts section -->
      <div v-if="emergency.length" class="bg-white rounded-2xl border border-red-100 shadow-sm overflow-hidden">
        <p class="text-xs font-semibold text-red-500 uppercase tracking-wider px-4 pt-3 pb-1">Emergency contacts</p>
        <ul class="divide-y divide-stone-50">
          <li v-for="p in emergency" :key="p.id">
            <RouterLink :to="`/people/${p.id}/edit`" class="flex items-center gap-3 px-4 py-3.5 hover:bg-stone-50 transition-colors">
              <div class="w-9 h-9 rounded-full bg-red-100 flex items-center justify-center shrink-0">
                <i class="ph ph-first-aid text-red-500 text-lg"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-stone-800 truncate">{{ p.name }}</p>
                <p class="text-xs text-stone-400 truncate">{{ [p.relationship, p.phone].filter(Boolean).join(' · ') }}</p>
              </div>
              <i class="ph ph-caret-right text-stone-300 shrink-0"></i>
            </RouterLink>
          </li>
        </ul>
      </div>

      <!-- All people -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden">
        <ul class="divide-y divide-stone-50">
          <li v-for="p in others" :key="p.id">
            <RouterLink :to="`/people/${p.id}/edit`" class="flex items-center gap-3 px-4 py-3.5 hover:bg-stone-50 transition-colors">
              <div class="w-9 h-9 rounded-full bg-violet-100 flex items-center justify-center shrink-0">
                <span class="text-sm font-semibold text-violet-600">{{ p.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-stone-800 truncate">{{ p.name }}<span v-if="p.nickname" class="font-normal text-stone-400"> ({{ p.nickname }})</span></p>
                <p class="text-xs text-stone-400 truncate">{{ [p.relationship, p.phone].filter(Boolean).join(' · ') }}</p>
              </div>
              <i class="ph ph-caret-right text-stone-300 shrink-0"></i>
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getPeople } from '@/api/people'

const people = ref([])
const loading = ref(true)

const emergency = computed(() => people.value.filter(p => p.emergency_contact))
const others = computed(() => people.value.filter(p => !p.emergency_contact))

onMounted(async () => {
  people.value = await getPeople().catch(() => [])
  loading.value = false
})
</script>
