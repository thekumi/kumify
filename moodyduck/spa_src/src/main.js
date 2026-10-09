import { createApp, h, markRaw } from 'vue'
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

window.__moodyduck = {
  vue: { h, markRaw },
  router,
  addNavItem: (item) => pluginsStore.addNavItem(item),
  components: { TopBar: markRaw(TopBar), BottomNav: markRaw(BottomNav) },
}

async function loadPlugins() {
  if (!isLoggedIn()) return
  const headers = { Authorization: `Token ${localStorage.getItem('authToken')}` }

  let modules = []
  try {
    const res = await fetch('/api/modules/', { headers })
    if (res.ok) modules = await res.json()
  } catch { /* non-fatal */ }

  pluginsStore.setVisibility(modules)

  for (const mod of modules) {
    if (!mod.bundle_url) continue
    try {
      const plugin = await import(/* @vite-ignore */ mod.bundle_url)
      if (typeof plugin.install === 'function') plugin.install(window.__moodyduck)
    } catch (e) {
      console.warn(`Failed to load plugin bundle for ${mod.slug}:`, e)
    }
  }

  try {
    const res = await fetch('/api/nav-order/', { headers })
    if (res.ok) pluginsStore.setNavOrder(await res.json())
  } catch { /* non-fatal */ }
}

loadPlugins().finally(() => app.mount('#app'))
