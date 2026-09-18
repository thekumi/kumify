<template>
  <div class="pb-nav">
    <TopBar title="Profile" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Account</p>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Display name</label>
          <input v-model="form.display_name" type="text" placeholder="How should we call you?"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Email address</label>
          <input v-model="form.email" type="email" placeholder="you@example.com"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Time zone</label>
          <input v-model="form.timezone" type="text" placeholder="e.g. Europe/Vienna"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Personal <span class="normal-case font-normal text-stone-400">— encrypted</span></p>
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

      <p v-if="!ks.dataKey" class="text-xs text-stone-400 text-center">Unlock your keystore to save encrypted fields.</p>
      <p v-if="saved" class="text-sm text-green-700 bg-green-50 rounded-xl px-4 py-3">Saved!</p>
      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { useAuthStore } from '@/stores/auth'
import { useKeystoreStore } from '@/stores/keystore'
import { decryptPayload } from '@/keystore/fields'

const auth = useAuthStore()
const ks = useKeystoreStore()
const form = ref({ display_name: '', email: '', timezone: '', legal_name: '', date_of_birth: '', phone: '', address: '' })
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
let rawProfile = null

async function applyDecryption() {
  if (!rawProfile || !ks.dataKey) return
  const dec = rawProfile.encrypted_payload
    ? await decryptPayload(ks.dataKey, rawProfile.encrypted_payload).catch(() => ({}))
    : {}
  form.value.legal_name    = dec.legal_name    ?? rawProfile.legal_name    ?? ''
  form.value.date_of_birth = dec.date_of_birth ?? rawProfile.date_of_birth ?? ''
  form.value.phone         = dec.phone         ?? rawProfile.phone         ?? ''
  form.value.address       = dec.address       ?? rawProfile.address       ?? ''
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

async function save() {
  saving.value = true; error.value = ''; saved.value = false
  try {
    const patch = {
      display_name: form.value.display_name || null,
      timezone:     form.value.timezone     || null,
      email:        form.value.email        || undefined,
      legal_name:   null,
      date_of_birth: null,
      phone:        null,
      address:      null,
    }
    if (ks.dataKey) {
      patch.encrypted_payload = await ks.encryptPayload({
        legal_name:    form.value.legal_name,
        date_of_birth: form.value.date_of_birth,
        phone:         form.value.phone,
        address:       form.value.address,
      })
    }
    rawProfile = await updateProfile(patch)
    await auth.init()
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

onMounted(async () => {
  rawProfile = await getProfile()
  form.value.display_name  = rawProfile.display_name  ?? ''
  form.value.email         = rawProfile.email         ?? ''
  form.value.timezone      = rawProfile.timezone      ?? ''
  form.value.legal_name    = rawProfile.legal_name    ?? ''
  form.value.date_of_birth = rawProfile.date_of_birth ?? ''
  form.value.phone         = rawProfile.phone         ?? ''
  form.value.address       = rawProfile.address       ?? ''
  await applyDecryption()
  loading.value = false
})
</script>
