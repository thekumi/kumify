import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePluginPermissionsStore = defineStore('pluginPermissions', () => {
  const pending = ref(null)
  return { pending }
})
