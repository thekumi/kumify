<template>
  <div class="pb-nav">
    <TopBar title="Mood Settings" :back="true" />

    <ul class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
      <li>
        <RouterLink to="/mood/settings/moods" class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
          <div class="w-9 h-9 rounded-full bg-clay-100 flex items-center justify-center shrink-0">
            <i class="ph ph-smiley text-clay-600 text-lg"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-stone-800">Moods</p>
            <p class="text-xs text-stone-400 mt-0.5">Manage your mood options</p>
          </div>
          <i class="ph ph-caret-right text-stone-300"></i>
        </RouterLink>
      </li>
      <li>
        <RouterLink to="/mood/settings/activities" class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
          <div class="w-9 h-9 rounded-full bg-sage-100 flex items-center justify-center shrink-0">
            <i class="ph ph-star text-sage-600 text-lg"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-stone-800">Activities</p>
            <p class="text-xs text-stone-400 mt-0.5">Manage your activity list</p>
          </div>
          <i class="ph ph-caret-right text-stone-300"></i>
        </RouterLink>
      </li>
    </ul>

    <BottomNav />
  </div>
</template>

<script setup>
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
</script>
