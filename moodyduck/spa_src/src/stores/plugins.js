import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const CORE_TABS = [
  { to: '/',        label: 'Home',    icon: 'ph ph-house' },
  { to: '/journal', label: 'Journal', icon: 'ph ph-book-open' },
  { to: '/health',  label: 'Health',  icon: 'ph ph-heartbeat' },
  { to: '/people',  label: 'People',  icon: 'ph ph-users' },
  { to: '/planner', label: 'Planner', icon: 'ph ph-calendar-dots' },
  { to: '/me',      label: 'Me',      icon: 'ph ph-user-circle' },
]

export const usePluginsStore = defineStore('plugins', () => {
  const navItems    = ref([])
  const modules     = ref([])  // raw list from /api/modules/
  const visibility  = ref({})  // nav_path → bool, from /api/modules/
  const navOrder    = ref([])  // ordered list of `to` paths, from /api/nav-order/

  function addNavItem(item) {
    navItems.value.push(item)
  }

  function setModules(mods) {
    modules.value = mods
  }

  function setVisibility(mods) {
    visibility.value = Object.fromEntries(mods.map(m => [m.nav_path, m.visible]))
  }

  function setNavOrder(order) {
    navOrder.value = order
  }

  const allNavItems = computed(() => [
    ...CORE_TABS.map(t => ({ ...t, core: true })),
    ...navItems.value.map(t => ({
      ...t,
      core: false,
      visible: visibility.value[t.to] ?? true,
    })),
  ])

  const allNavItemsOrdered = computed(() => {
    const items = allNavItems.value
    if (!navOrder.value.length) return items
    const pos = Object.fromEntries(navOrder.value.map((key, i) => [key, i]))
    return [...items].sort((a, b) => (pos[a.to] ?? 999) - (pos[b.to] ?? 999))
  })

  const orderedVisibleNavItems = computed(() =>
    allNavItemsOrdered.value.filter(item => item.core || item.visible !== false)
  )

  return {
    navItems,
    modules,
    addNavItem,
    setModules,
    setVisibility,
    setNavOrder,
    allNavItemsOrdered,
    orderedVisibleNavItems,
  }
})
