<template>
  <div class="pb-nav">
    <TopBar title="Navigation" :back="true" />

    <div class="px-4 py-4 space-y-4">

      <p class="text-sm text-stone-500">
        Drag items to reorder. Toggle visibility for installed modules.
      </p>

      <div v-if="loading" class="flex justify-center py-12">
        <div class="w-7 h-7 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
      </div>

      <div v-else
        class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden divide-y divide-stone-50"
        @dragover.prevent
        @drop.prevent="onDrop"
      >
        <div
          v-for="(item, index) in localItems"
          :key="item.to"
          draggable="true"
          @dragstart="onDragStart(index, $event)"
          @dragenter.prevent="onDragEnter(index)"
          @dragend="onDragEnd"
          class="flex items-center gap-3 px-4 py-3.5 transition-colors"
          :class="dragOverIndex === index ? 'bg-clay-50' : ''"
        >
          <i class="ph ph-dots-six-vertical text-xl text-stone-300 cursor-grab shrink-0"></i>

          <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
            :class="item.core ? 'bg-stone-100' : 'bg-clay-100'">
            <i :class="[item.icon, 'text-base', item.core ? 'text-stone-500' : 'text-clay-600']"></i>
          </div>

          <p class="flex-1 text-sm font-medium text-stone-700">{{ item.label }}</p>

          <span v-if="item.core" class="text-xs text-stone-300 shrink-0">always shown</span>
          <button v-else type="button" @click="toggleVisible(item)"
            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
            :class="item.visible !== false ? 'bg-clay-600' : 'bg-stone-200'">
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
              :class="item.visible !== false ? 'translate-x-5' : 'translate-x-0'"></span>
          </button>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { setModuleVisible, setNavOrder } from '@/api/modules'
import { usePluginsStore } from '@/stores/plugins'

const pluginsStore = usePluginsStore()
const localItems = ref([])
const loading = ref(true)
const error = ref('')

let dragIndex = null
const dragOverIndex = ref(null)

function onDragStart(index, event) {
  dragIndex = index
  event.dataTransfer.effectAllowed = 'move'
}

function onDragEnter(index) {
  if (dragIndex === null || dragIndex === index) return
  const items = [...localItems.value]
  const [moved] = items.splice(dragIndex, 1)
  items.splice(index, 0, moved)
  localItems.value = items
  dragIndex = index
  dragOverIndex.value = index
}

async function onDragEnd() {
  dragIndex = null
  dragOverIndex.value = null
  await saveOrder()
  pluginsStore.setNavOrder(localItems.value.map(i => i.to))
}

function onDrop() {
  dragOverIndex.value = null
}

async function toggleVisible(item) {
  const slug = item.to.split('/').pop()
  const next = item.visible === false
  item.visible = next
  try {
    await setModuleVisible(slug, next)
    pluginsStore.setVisibility(
      localItems.value
        .filter(i => !i.core)
        .map(i => ({ nav_path: i.to, visible: i.visible !== false }))
    )
  } catch {
    item.visible = !next
    error.value = 'Could not update visibility.'
    setTimeout(() => { error.value = '' }, 3000)
  }
}

async function saveOrder() {
  try {
    await setNavOrder(localItems.value.map(i => i.to))
  } catch {
    error.value = 'Could not save order.'
    setTimeout(() => { error.value = '' }, 3000)
  }
}

onMounted(() => {
  localItems.value = pluginsStore.allNavItemsOrdered.map(item => ({ ...item }))
  loading.value = false
})
</script>
