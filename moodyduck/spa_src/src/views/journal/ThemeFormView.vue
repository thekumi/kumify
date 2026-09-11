<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Theme' : 'New Theme'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
          <input v-model="form.name" type="text" required placeholder="e.g. Flying"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Icon class <span class="font-normal text-xs">(Phosphor CSS class)</span></label>
          <div class="flex items-center gap-3">
            <input v-model="form.icon" type="text" placeholder="ph ph-tag"
              class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
            <i :class="form.icon || 'ph ph-tag'" :style="form.color ? `color:${form.color}` : ''" class="text-3xl shrink-0"></i>
          </div>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Color</label>
          <div class="flex items-center gap-3">
            <input v-model="form.color" type="color"
              class="w-10 h-10 rounded-xl border border-stone-200 cursor-pointer p-0.5 bg-stone-50" />
            <span class="text-sm text-stone-500 font-mono">{{ form.color }}</span>
          </div>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Create theme') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete theme
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getThemes, createTheme, updateTheme, deleteTheme } from '@/api/dreams'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', icon: 'ph ph-tag', color: '#6366f1' })
const saving = ref(false)
const error = ref('')

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) await updateTheme(id, form.value)
    else await createTheme(form.value)
    router.push('/journal/dreams/themes')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this theme?')) return
  await deleteTheme(id)
  router.push('/journal/dreams/themes')
}

onMounted(async () => {
  if (id) {
    const themes = await getThemes()
    const t = themes.find(t => String(t.id) === String(id))
    if (t) form.value = { name: t.name, icon: t.icon || 'ph ph-tag', color: t.color || '#6366f1' }
  }
})
</script>
