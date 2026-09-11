<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Medication' : 'New Medication'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
          <input v-model="form.name" type="text" placeholder="e.g. Ibuprofen 400mg"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Current supply</label>
          <input v-model.number="form.supply" type="number" step="0.5" min="0" placeholder="e.g. 30"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Remarks</label>
          <textarea v-model="form.remarks" rows="3" placeholder="Instructions, notes…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.prn" type="checkbox" class="w-4 h-4 rounded accent-blue-600" />
          <span class="text-sm text-stone-700 font-medium">As needed (PRN)</span>
        </label>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add medication') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete medication
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getMedications, createMedication, updateMedication, deleteMedication } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', supply: null, prn: false, remarks: '' })
const saving = ref(false)
const error = ref('')
let rawMedication = null

async function fillForm(m) {
  const dec = await ks.decrypt(m)
  form.value = { name: dec.name ?? '', supply: dec.supply, prn: dec.prn ?? false, remarks: dec.remarks ?? '' }
}

watch(() => ks.dataKey, async (key) => { if (key && rawMedication) await fillForm(rawMedication) })

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) await saveEncrypted(updateMedication, id, form.value, ['name', 'remarks'], rawMedication, ks)
    else await createMedication(form.value)
    router.push('/health/medications')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this medication?')) return
  await deleteMedication(id)
  router.push('/health/medications')
}

onMounted(async () => {
  if (id) {
    const all = await getMedications()
    rawMedication = all.find(m => String(m.id) === String(id))
    if (rawMedication) await fillForm(rawMedication)
  }
})
</script>
