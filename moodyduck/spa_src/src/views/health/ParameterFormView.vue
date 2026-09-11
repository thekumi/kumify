<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Parameter' : 'New Parameter'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
          <input v-model="form.name" type="text" required placeholder="e.g. Blood pressure, Weight"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Unit <span class="font-normal">(optional)</span></label>
          <input v-model="form.unit" type="text" placeholder="e.g. mmHg, kg, bpm"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Icon class <span class="font-normal text-xs">(Phosphor CSS class)</span></label>
          <div class="flex items-center gap-3">
            <input v-model="form.icon" type="text" placeholder="ph ph-heart"
              class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-stone-800 bg-stone-50 text-sm" />
            <i :class="form.icon || 'ph ph-heart'" class="text-3xl text-green-600 shrink-0"></i>
          </div>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Create parameter') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete parameter
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
import { getParameters, createParameter, updateParameter, deleteParameter } from '@/api/health'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', unit: '', icon: 'ph ph-heart' })
const saving = ref(false)
const error = ref('')

async function save() {
  saving.value = true; error.value = ''
  try {
    const payload = { name: form.value.name, unit: form.value.unit || null, icon: form.value.icon || 'ph ph-heart' }
    if (id) await updateParameter(id, payload)
    else await createParameter(payload)
    router.push('/health/parameters')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this parameter? Existing log records for it will also be removed.')) return
  await deleteParameter(id)
  router.push('/health/parameters')
}

onMounted(async () => {
  if (id) {
    const all = await getParameters()
    const p = all.find(p => String(p.id) === String(id))
    if (p) form.value = { name: p.name, unit: p.unit ?? '', icon: p.icon || 'ph ph-heart' }
  }
})
</script>
