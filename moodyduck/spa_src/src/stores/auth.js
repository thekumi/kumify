import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMe, isLoggedIn, logout as apiLogout } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const ready = ref(false)

  async function init() {
    if (!isLoggedIn()) { ready.value = true; return }
    try {
      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), 10000)
      try {
        user.value = await getMe(controller.signal)
      } finally {
        clearTimeout(timer)
      }
    } catch {
      // Any failure (network error, server error, timeout) — trust the cached
      // token so the keystore can boot from IndexedDB and the app works offline.
      user.value = {}
    }
    if (user.value !== null) {
      window.Android?.notifyLogin?.(localStorage.getItem('authToken') ?? '')
    }
    ready.value = true
  }

  function logout() {
    apiLogout()
    user.value = null
    window.Android?.notifyLogout?.()
  }

  return { user, ready, init, logout }
})
