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
    } catch {
      user.value = null
    }
    ready.value = true
  }

  function logout() {
    apiLogout()
    user.value = null
  }

  return { user, ready, init, logout }
})
