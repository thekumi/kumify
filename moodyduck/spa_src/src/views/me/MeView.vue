<template>
  <div class="pb-nav">
    <TopBar title="Me" />

    <div class="px-4 py-4 space-y-3">
      <!-- User card -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5 flex items-center gap-4">
        <div class="w-14 h-14 rounded-full bg-clay-100 flex items-center justify-center shrink-0">
          <i class="ph ph-user text-3xl text-clay-600"></i>
        </div>
        <div>
          <p class="font-semibold text-stone-800 text-lg">{{ auth.user?.display_name || auth.user?.username || '…' }}</p>
          <p class="text-sm text-stone-400">{{ auth.user?.email }}</p>
        </div>
      </div>

      <!-- Navigation links -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden divide-y divide-stone-50">
        <RouterLink v-for="item in links" :key="item.to" :to="item.to"
          class="flex items-center gap-3 px-4 py-4 hover:bg-stone-50 transition-colors">
          <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" :class="item.bg">
            <i :class="[item.icon, item.color, 'text-lg']"></i>
          </div>
          <p class="flex-1 text-sm font-medium text-stone-700">{{ item.label }}</p>
          <i class="ph ph-caret-right text-stone-300"></i>
        </RouterLink>
      </div>

      <!-- Logout -->
      <button @click="handleLogout"
        class="w-full py-3.5 rounded-2xl border border-red-100 bg-white text-red-600 text-sm font-semibold hover:bg-red-50 transition-colors">
        Sign out
      </button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const links = [
  { to: '/me/profile',    label: 'Profile',              icon: 'ph ph-identification-card', bg: 'bg-clay-100',   color: 'text-clay-600' },
  { to: '/me/devices',    label: 'Devices & Keys',       icon: 'ph ph-devices',             bg: 'bg-blue-100',   color: 'text-blue-600' },
  { to: '/me/key-backup', label: 'Key Backup',           icon: 'ph ph-shield-check',        bg: 'bg-green-100',  color: 'text-green-600' },
  { to: '/me/security',   label: 'Privacy & Security',   icon: 'ph ph-lock',                bg: 'bg-amber-100',  color: 'text-amber-600' },
  { to: '/me/emergency',  label: 'Emergency Info',        icon: 'ph ph-first-aid',           bg: 'bg-red-100',    color: 'text-red-600' },
  { to: '/people',        label: 'People',               icon: 'ph ph-users',               bg: 'bg-violet-100', color: 'text-violet-600' },
]

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
