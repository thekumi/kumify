<template>
  <div class="pb-nav">
    <TopBar title="Module Admin" :back="true" />

    <div class="px-4 py-4 space-y-4">

      <div v-if="loading" class="flex justify-center py-12">
        <div class="w-7 h-7 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
      </div>

      <template v-else>
        <div v-if="!modules.length"
          class="bg-white rounded-2xl border border-stone-100 shadow-sm px-4 py-8 text-center">
          <i class="ph ph-puzzle-piece text-3xl text-stone-300 block mb-2"></i>
          <p class="text-sm text-stone-400">No modules installed.</p>
        </div>

        <div v-for="mod in modules" :key="mod.slug"
          class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">

          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-clay-100 flex items-center justify-center shrink-0">
              <i :class="[mod.icon, 'text-lg text-clay-600']"></i>
            </div>
            <div>
              <p class="text-sm font-semibold text-stone-800">{{ mod.name }}</p>
              <p class="text-xs text-stone-400 font-mono mt-0.5">{{ mod.slug }}</p>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-2">Who can use this</p>
              <div class="flex rounded-xl border border-stone-200 overflow-hidden text-sm font-medium">
                <button v-for="opt in enabledForOptions" :key="opt.value"
                  type="button"
                  @click="setProp(mod, 'enabled_for', opt.value)"
                  class="flex-1 py-2 transition-colors"
                  :class="mod.enabled_for === opt.value
                    ? 'bg-clay-600 text-white'
                    : 'bg-white text-stone-500 hover:bg-stone-50'">
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-stone-700">Shown by default</p>
                <p class="text-xs text-stone-400 mt-0.5">New users see this in their nav without opting in</p>
              </div>
              <button type="button" @click="setProp(mod, 'shown_by_default', !mod.shown_by_default)"
                class="relative w-11 h-6 rounded-full transition-colors shrink-0"
                :class="mod.shown_by_default ? 'bg-clay-600' : 'bg-stone-200'">
                <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                  :class="mod.shown_by_default ? 'translate-x-5' : 'translate-x-0'"></span>
              </button>
            </div>
          </div>

          <p v-if="mod._error" class="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ mod._error }}</p>
          <p v-if="mod._saved" class="text-xs text-green-700 bg-green-50 rounded-lg px-3 py-2">Saved</p>
        </div>
      </template>

    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { adminGetModules, adminPatchModule } from '@/api/modules'

const modules = ref([])
const loading = ref(true)

const enabledForOptions = [
  { value: 'disabled', label: 'Nobody' },
  { value: 'staff',    label: 'Staff' },
  { value: 'all',      label: 'Everyone' },
]

async function setProp(mod, key, value) {
  const prev = mod[key]
  mod[key] = value
  mod._error = ''
  mod._saved = false
  try {
    await adminPatchModule(mod.slug, { [key]: value })
    mod._saved = true
    setTimeout(() => { mod._saved = false }, 2000)
  } catch {
    mod[key] = prev
    mod._error = 'Could not save.'
  }
}

onMounted(async () => {
  try {
    const data = await adminGetModules()
    modules.value = data.map(m => ({ ...m, _error: '', _saved: false }))
  } catch {
    // 403 for non-staff — shouldn't reach this view, but handle gracefully
  } finally {
    loading.value = false
  }
})
</script>
