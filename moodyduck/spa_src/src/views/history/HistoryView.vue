<template>
  <div class="pb-nav">
    <TopBar title="History" :back="true" />

    <div class="px-4 py-4 space-y-3">
      <RouterLink to="/journal/history/stats"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-violet-100 flex items-center justify-center shrink-0">
          <i class="ph ph-chart-line text-2xl text-violet-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Statistics</p>
          <p class="text-sm text-stone-400 mt-0.5">Mood trends, activities and habits over time</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>

      <RouterLink to="/journal/history/gallery"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-rose-100 flex items-center justify-center shrink-0">
          <i class="ph ph-images text-2xl text-rose-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Media Gallery</p>
          <p class="text-sm text-stone-400 mt-0.5">All photos and files from your journal</p>
        </div>
        <i class="ph ph-caret-right text-stone-300"></i>
      </RouterLink>

      <RouterLink to="/journal/history/memories"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center shrink-0">
          <i class="ph ph-shooting-star text-2xl text-amber-600"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">Memories</p>
          <p class="text-sm text-stone-400 mt-0.5">On this day in the past</p>
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
