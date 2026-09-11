<template>
  <div class="pb-nav">
    <TopBar title="Emergency Info" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="save" class="px-4 py-4 space-y-3">
      <!-- Personal -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Personal</p>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Legal name</label>
          <input v-model="form.legal_name" type="text" placeholder="Full legal name"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Date of birth</label>
          <input v-model="form.date_of_birth" type="date"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Phone</label>
          <input v-model="form.phone" type="tel" placeholder="+1 555 000 0000"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Address</label>
          <textarea v-model="form.address" rows="2" placeholder="Street, city, country"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
      </div>

      <!-- Medical -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Medical</p>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Blood type</label>
          <select v-model="form.blood_type"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm">
            <option value="">Unknown</option>
            <option v-for="bt in bloodTypes" :key="bt" :value="bt">{{ bt }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Allergies</label>
          <textarea v-model="form.allergies" rows="3" placeholder="List any known allergies…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Medical notes</label>
          <textarea v-model="form.medical_notes" rows="3" placeholder="Conditions, medications, instructions…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
      </div>

      <p v-if="saved" class="text-sm text-green-700 bg-green-50 rounded-xl px-4 py-3">Saved!</p>
      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving || !ks.dataKey"
        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>

      <p v-if="!ks.dataKey" class="text-xs text-stone-400 text-center">Unlock your keystore to save.</p>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getEmergencyProfile, updateEmergencyProfile } from '@/api/profile'
import { useKeystoreStore } from '@/stores/keystore'
import { decryptPayload } from '@/keystore/fields'

const EMERGENCY_CACHE_KEY = 'ks:emergency-profile'
const ks = useKeystoreStore()
const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const form = ref({ legal_name: '', date_of_birth: '', phone: '', address: '', blood_type: '', allergies: '', medical_notes: '' })
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
let raw = null

async function applyDecryption() {
  if (!raw || !ks.dataKey) return
  const profilePlain = raw.profile_encrypted_payload
    ? await decryptPayload(ks.dataKey, raw.profile_encrypted_payload).catch(() => ({}))
    : {}
  const medicalPlain = raw.medical_encrypted_payload
    ? await decryptPayload(ks.dataKey, raw.medical_encrypted_payload).catch(() => ({}))
    : {}
  const plain = {
    legal_name: profilePlain.legal_name ?? '',
    date_of_birth: profilePlain.date_of_birth ?? '',
    phone: profilePlain.phone ?? '',
    address: profilePlain.address ?? '',
    blood_type: medicalPlain.blood_type ?? '',
    allergies: medicalPlain.allergies ?? '',
    medical_notes: medicalPlain.medical_notes ?? '',
  }
  form.value = plain
  // Update the offline cache with fresh plaintext
  localStorage.setItem(EMERGENCY_CACHE_KEY, JSON.stringify({
    ...plain,
    display_name: raw.display_name,
    contacts: raw.contacts,
    vaccinations: raw.vaccinations,
  }))
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

async function save() {
  saving.value = true; error.value = ''; saved.value = false
  try {
    const profileFields = { legal_name: form.value.legal_name, phone: form.value.phone, address: form.value.address, date_of_birth: form.value.date_of_birth }
    const medicalFields = { blood_type: form.value.blood_type, allergies: form.value.allergies, medical_notes: form.value.medical_notes }

    const [profilePayload, medicalPayload] = await Promise.all([
      ks.encryptPayload(profileFields),
      ks.encryptPayload(medicalFields),
    ])

    raw = await updateEmergencyProfile({
      profile_encrypted_payload: profilePayload,
      medical_encrypted_payload: medicalPayload,
    })

    // Refresh the offline cache
    localStorage.setItem(EMERGENCY_CACHE_KEY, JSON.stringify({
      ...form.value,
      display_name: raw.display_name,
      contacts: raw.contacts,
      vaccinations: raw.vaccinations,
    }))

    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

onMounted(async () => {
  raw = await getEmergencyProfile().catch(() => null)
  await applyDecryption()
  loading.value = false
})
</script>
