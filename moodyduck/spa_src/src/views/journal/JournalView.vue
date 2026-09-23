<template>
  <div class="pb-nav">
    <TopBar title="Journal">
      <template #actions>
        <RouterLink to="/mood/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-clay-100 hover:bg-clay-200 transition-colors">
          <i class="ph ph-plus text-clay-700"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div class="px-4 py-4 space-y-3">
      <RouterLink to="/mood"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-clay-100 flex items-center justify-center shrink-0">
          <i class="ph ph-smiley text-2xl text-clay-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Mood Log</p>
          <p class="text-sm text-stone-400 mt-0.5">Track how you feel throughout the day</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>

      <RouterLink to="/journal/dreams"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center shrink-0">
          <i class="ph ph-moon-stars text-2xl text-blue-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Dreams</p>
          <p class="text-sm text-stone-400 mt-0.5">Record your dreams and nighttime experiences</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>

      <RouterLink to="/journal/cbt"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-purple-100 flex items-center justify-center shrink-0">
          <i class="ph ph-brain text-2xl text-purple-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Thought Records</p>
          <p class="text-sm text-stone-400 mt-0.5">Cognitive behavioural therapy exercises</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>

      <RouterLink to="/journal/history"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center shrink-0">
          <i class="ph ph-clock-counter-clockwise text-2xl text-emerald-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">History</p>
          <p class="text-sm text-stone-400 mt-0.5">Stats, media gallery and memories</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
</script>
