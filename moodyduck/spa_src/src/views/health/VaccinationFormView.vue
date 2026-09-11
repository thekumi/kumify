<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Vaccination' : 'New Vaccination'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Vaccine name</label>
          <input v-model="form.name" type="text" required placeholder="e.g. MMR"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Target disease</label>
          <input v-model="form.target_disease" type="text" placeholder="e.g. Measles, Mumps, Rubella"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Date administered</label>
          <input v-model="form.administered_on" type="date" required
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Next due date <span class="font-normal">(optional)</span></label>
          <input v-model="form.next_due" type="date"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Provider</label>
          <input v-model="form.provider" type="text" placeholder="e.g. Dr. Smith"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Batch number</label>
          <input v-model="form.batch_number" type="text" placeholder="Batch / lot number"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add vaccination') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete vaccination
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
import { getVaccinations, createVaccination, updateVaccination, deleteVaccination } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', target_disease: '', administered_on: '', next_due: '', provider: '', batch_number: '' })
const saving = ref(false)
const error = ref('')
let rawVaccination = null
let hiddenNotes = null

const ENCRYPTED_FIELDS = ['name', 'target_disease', 'provider', 'batch_number', 'notes']

async function fillForm(v) {
  const dec = await ks.decrypt(v)
  form.value = {
    name: dec.name ?? '',
    target_disease: dec.target_disease ?? '',
    administered_on: dec.administered_on ?? '',
    next_due: dec.next_due ?? '',
    provider: dec.provider ?? '',
    batch_number: dec.batch_number ?? '',
  }
  hiddenNotes = dec.notes ?? null
}

watch(() => ks.dataKey, async (key) => { if (key && rawVaccination) await fillForm(rawVaccination) })

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) {
      const payload = { ...form.value, notes: hiddenNotes }
      if (!payload.next_due) payload.next_due = null
      await saveEncrypted(updateVaccination, id, payload, ENCRYPTED_FIELDS, rawVaccination, ks)
    } else {
      const payload = { ...form.value }
      if (!payload.next_due) payload.next_due = null
      await createVaccination(payload)
    }
    router.push('/health/vaccinations')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this vaccination?')) return
  await deleteVaccination(id)
  router.push('/health/vaccinations')
}

onMounted(async () => {
  if (id) {
    const all = await getVaccinations()
    rawVaccination = all.find(v => String(v.id) === String(id))
    if (rawVaccination) await fillForm(rawVaccination)
  }
})
</script>
