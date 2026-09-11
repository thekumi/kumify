<template>
  <nav class="fixed bottom-0 inset-x-0 bg-white border-t border-stone-100 safe-bottom z-50">
    <div class="flex items-center h-16">
      <RouterLink
        v-for="item in tabs"
        :key="item.to"
        :to="item.to"
        class="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-xs font-medium transition-colors"
        :class="isActive(item) ? 'text-clay-600' : 'text-stone-400 hover:text-stone-600'"
      >
        <i :class="[item.icon, 'text-2xl leading-none']"></i>
        <span>{{ item.label }}</span>
      </RouterLink>
      <button @click="ks.lock()"
        class="w-12 flex flex-col items-center justify-center gap-0.5 py-2 text-stone-300 hover:text-stone-500 transition-colors"
        title="Lock">
        <i class="ph ph-lock-simple text-2xl leading-none"></i>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const route = useRoute()

const tabs = [
  { to: '/',        label: 'Home',    icon: 'ph ph-house' },
  { to: '/mood',    label: 'Mood',    icon: 'ph ph-smiley' },
  { to: '/journal', label: 'Journal', icon: 'ph ph-book-open' },
  { to: '/health',  label: 'Health',  icon: 'ph ph-heartbeat' },
  { to: '/me',      label: 'Me',      icon: 'ph ph-user-circle' },
]

function isActive(item) {
  if (item.to === '/') return route.path === '/'
  return route.path.startsWith(item.to)
}
</script>
