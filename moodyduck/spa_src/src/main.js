import * as _vue from 'vue'
import * as _vueRouter from 'vue-router'
import { createApp, h, markRaw, watch } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@phosphor-icons/web/regular'
import { isLoggedIn } from '@/api/auth'
import { usePluginsStore } from '@/stores/plugins'
import { useKeystoreStore } from '@/stores/keystore'
import { usePluginPermissionsStore } from '@/stores/pluginPermissions'
import { registerCalendarProvider, registerTaskListProvider } from '@/planner/registry'
import '@/views/health/plannerProviders'
import '@/views/people/plannerProviders'
import '@/views/mood/plannerProviders'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {})
  })
}

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const pluginsStore = usePluginsStore(pinia)

const _keystoreCapability = {
  get status() { return useKeystoreStore(pinia).status },
  encrypt:    (fields) => useKeystoreStore(pinia).encryptPayload(fields),
  decrypt:    (item)   => useKeystoreStore(pinia).decrypt(item),
  decryptAll: (items)  => useKeystoreStore(pinia).decryptAll(items),
}

window.__moodyduck = {
  vue: _vue,
  vueRouter: _vueRouter,
  router,
  addNavItem: (item) => pluginsStore.addNavItem(item),
  registerCalendarProvider,
  registerTaskListProvider,
  components: { TopBar: markRaw(TopBar), BottomNav: markRaw(BottomNav) },
}

function _makeRequestKeystore(slug, pluginName) {
  return () => new Promise((resolve) => {
    const key = `moodyduck:perm:${slug}:keystore`
    const stored = localStorage.getItem(key)
    if (stored === 'granted') { resolve(_keystoreCapability); return }
    if (stored === 'denied') { resolve(null); return }
    const permStore = usePluginPermissionsStore(pinia)
    permStore.pending = {
      pluginName,
      grant(remember) {
        if (remember) localStorage.setItem(key, 'granted')
        permStore.pending = null
        resolve(_keystoreCapability)
      },
      deny(remember) {
        if (remember) localStorage.setItem(key, 'denied')
        permStore.pending = null
        resolve(null)
      },
    }
  })
}

async function loadPlugins() {
  if (!isLoggedIn()) return
  const headers = { Authorization: `Token ${localStorage.getItem('authToken')}` }

  let modules = []
  try {
    const res = await fetch('/api/modules/', { headers })
    if (res.ok) modules = await res.json()
  } catch { /* non-fatal */ }

  pluginsStore.setModules(modules)
  pluginsStore.setVisibility(modules)

  for (const mod of modules) {
    if (!mod.bundle_url) continue
    try {
      const plugin = await import(/* @vite-ignore */ mod.bundle_url)
      if (typeof plugin.install === 'function') {
        await plugin.install({
          ...window.__moodyduck,
          requestKeystore: _makeRequestKeystore(mod.slug, mod.name || mod.slug),
        })
      }
    } catch (e) {
      console.warn(`Failed to load plugin bundle for ${mod.slug}:`, e)
    }
  }

  try {
    const res = await fetch('/api/nav-order/', { headers })
    if (res.ok) pluginsStore.setNavOrder(await res.json())
  } catch { /* non-fatal */ }
}

let pluginsLoaded = false
watch(
  () => useKeystoreStore(pinia).status,
  async (status) => {
    if (status === 'ready' && !pluginsLoaded) {
      pluginsLoaded = true
      await loadPlugins()
    }
  }
)

app.mount('#app')
