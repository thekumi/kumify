<template>
  <div class="pb-nav">
    <TopBar title="Health" />

    <div class="px-4 py-4 space-y-3">
      <RouterLink v-for="item in sections" :key="item.to" :to="item.to"
        class="flex items-center gap-4 bg-white rounded-2xl border border-stone-100 shadow-sm p-5 hover:bg-stone-50 transition-colors">
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0" :class="item.bg">
          <i :class="[item.icon, 'text-2xl', item.iconColor]"></i>
        </div>
        <div class="flex-1">
          <p class="font-semibold text-stone-800">{{ item.label }}</p>
          <p class="text-sm text-stone-400 mt-0.5">{{ item.desc }}</p>
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

const sections = [
  { to: '/health/logs',         label: 'Health Logs',    desc: 'Track your vital signs and measurements',    icon: 'ph ph-heartbeat',    bg: 'bg-green-100', iconColor: 'text-green-600' },
  { to: '/health/medications',  label: 'Medications',    desc: 'Manage your medications and schedules',      icon: 'ph ph-pill',         bg: 'bg-blue-100',  iconColor: 'text-blue-600' },
  { to: '/health/vaccinations', label: 'Vaccinations',   desc: 'Keep track of your vaccination history',     icon: 'ph ph-syringe',      bg: 'bg-purple-100',iconColor: 'text-purple-600' },
  { to: '/health/habits',       label: 'Habits',         desc: 'Build and track daily habits',               icon: 'ph ph-check-circle', bg: 'bg-amber-100',  iconColor: 'text-amber-600' },
  { to: '/health/parameters',  label: 'Parameters',     desc: 'Define what you track in health logs',        icon: 'ph ph-chart-line',   bg: 'bg-teal-100',   iconColor: 'text-teal-600' },
]
</script>
