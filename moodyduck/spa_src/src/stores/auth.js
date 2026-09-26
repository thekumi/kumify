import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMe, isLoggedIn, logout as apiLogout } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const ready = ref(false)

  async function init() {
    if (!isLoggedIn()) { ready.value = true; return }
    try {
      user.value = await getMe()
    } catch (e) {
      // Network unavailable — treat the stored token as still valid so the
      // keystore can boot from its IndexedDB-cached key and the app works offline.
      user.value = e instanceof TypeError ? {} : null
    }
    ready.value = true
  }

  function logout() {
    apiLogout()
    user.value = null
  }

  return { user, ready, init, logout }
})
