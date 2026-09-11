<template>
  <!-- Lock screen -->
  <Teleport to="body">
    <div v-if="ks.status === 'locked'"
         class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-clay-50 px-6">
      <div class="w-20 h-20 rounded-full bg-clay-200 flex items-center justify-center mb-6">
        <DuckIcon bg="#f4d2ba" class="w-10 h-10 text-clay-700"/>
      </div>
      <h1 class="text-xl font-bold text-stone-800 mb-2">MoodyDuck is locked</h1>
      <p class="text-sm text-stone-400 mb-8 text-center">
        {{ ks.lockConfigured ? 'Enter your lock PIN to continue.' : 'Tap Unlock to continue.' }}
      </p>

      <div class="w-full max-w-xs space-y-3">
        <input
          v-if="ks.lockConfigured"
          ref="pinRef"
          v-model="lockPin"
          type="password"
          placeholder="Lock PIN"
          autocomplete="current-password"
          @keydown.enter="submitUnlock"
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-white text-sm"
        />

        <p v-if="lockError" class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ lockError }}</p>

        <button @click="submitUnlock" :disabled="unlocking || (ks.lockConfigured && !lockPin)"
          class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
          {{ unlocking ? 'Unlocking…' : 'Unlock' }}
        </button>

        <button type="button" @click="toggleEmergency"
          class="w-full py-2.5 rounded-xl border border-red-200 bg-white text-red-600 text-sm font-medium hover:bg-red-50 transition-colors flex items-center justify-center gap-2">
          <i class="ph ph-first-aid text-base"></i>
          Emergency Info
        </button>
      </div>

      <!-- Emergency info panel -->
      <div v-if="showEmergency" class="w-full max-w-xs mt-4 bg-white rounded-2xl border border-red-100 shadow-sm p-4 text-sm space-y-2 max-h-72 overflow-y-auto">
        <div v-if="emergencyLoading" class="flex justify-center py-4">
          <div class="w-5 h-5 border-2 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
        </div>
        <template v-else-if="emergency">
          <p v-if="emergency.legal_name || emergency.display_name" class="font-semibold text-stone-800">{{ emergency.legal_name || emergency.display_name }}</p>
          <p v-if="emergency.date_of_birth" class="text-stone-500">DOB: {{ emergency.date_of_birth }}</p>
          <p v-if="emergency.blood_type" class="text-stone-500">Blood type: <span class="font-medium text-stone-700">{{ emergency.blood_type }}</span></p>
          <p v-if="emergency.phone" class="text-stone-500">Phone: {{ emergency.phone }}</p>
          <div v-if="emergency.allergies" class="pt-1">
            <p class="text-xs font-semibold text-red-600 uppercase tracking-wider mb-0.5">Allergies</p>
            <p class="text-stone-700 whitespace-pre-wrap">{{ emergency.allergies }}</p>
          </div>
          <div v-if="emergency.medical_notes" class="pt-1">
            <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-0.5">Medical notes</p>
            <p class="text-stone-700 whitespace-pre-wrap">{{ emergency.medical_notes }}</p>
          </div>
          <div v-if="emergency.contacts?.length" class="pt-1">
            <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-1">Emergency contacts</p>
            <div v-for="c in emergency.contacts" :key="c.id" class="text-stone-700">
              {{ c.name }}<span v-if="c.relationship" class="text-stone-400"> ({{ c.relationship }})</span><span v-if="c.phone"> · {{ c.phone }}</span>
            </div>
          </div>
          <p v-if="!hasAnyEmergencyData" class="text-stone-400 text-center py-2">No emergency info set up yet.</p>
        </template>
      </div>
    </div>
  </Teleport>

  <!-- Passphrase modal -->
  <Teleport to="body">
    <div v-if="ks.status === 'needs_passphrase'"
         class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-clay-100 flex items-center justify-center shrink-0">
            <i class="ph ph-lock-key text-clay-700 text-xl"></i>
          </div>
          <div>
            <h2 class="font-semibold text-stone-800">Unlock your data</h2>
            <p class="text-xs text-stone-400">Enter your recovery passphrase</p>
          </div>
        </div>

        <p class="text-sm text-stone-500 mb-4">
          This device doesn't have your encryption key yet. Enter your recovery passphrase to unlock your encrypted entries.
        </p>

        <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2 mb-3">{{ error }}</p>

        <input
          ref="inputRef"
          v-model="passphrase"
          type="password"
          placeholder="Recovery passphrase"
          autocomplete="current-password"
          @keydown.enter="submit"
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm mb-3"
        />

        <button @click="submit" :disabled="busy || !passphrase"
          class="w-full py-3 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors text-sm">
          {{ busy ? 'Unlocking…' : 'Unlock' }}
        </button>
      </div>
    </div>

    <!-- Waiting banner -->
    <div v-if="ks.status === 'waiting'"
         class="fixed top-0 inset-x-0 z-40 bg-amber-50 border-b border-amber-200 px-4 py-2.5 flex items-center gap-2 text-sm text-amber-800">
      <i class="ph ph-hourglass text-amber-600 text-base shrink-0"></i>
      <span><strong>Waiting for authorisation.</strong> Log in on a paired device to grant this device access to your encrypted data.</span>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { useKeystoreStore } from '@/stores/keystore'
import DuckIcon from '@/components/DuckIcon.vue'
import { getEmergencyProfile } from '@/api/profile'
import { decryptPayload } from '@/keystore/fields'

const ks = useKeystoreStore()

// Backup passphrase flow
const passphrase = ref('')
const busy = ref(false)
const error = ref('')
const inputRef = ref(null)

async function refreshEmergencyCache(dataKey) {
  try {
    const raw = await getEmergencyProfile()
    const profilePlain = raw.profile_encrypted_payload
      ? await decryptPayload(dataKey, raw.profile_encrypted_payload).catch(() => ({}))
      : {}
    const medicalPlain = raw.medical_encrypted_payload
      ? await decryptPayload(dataKey, raw.medical_encrypted_payload).catch(() => ({}))
      : {}
    localStorage.setItem(EMERGENCY_CACHE_KEY, JSON.stringify({
      display_name: raw.display_name,
      contacts: raw.contacts,
      vaccinations: raw.vaccinations,
      ...profilePlain,
      ...medicalPlain,
    }))
  } catch {}
}

watch(() => ks.status, async (s) => {
  if (s === 'needs_passphrase') {
    passphrase.value = ''
    error.value = ''
    nextTick(() => inputRef.value?.focus())
  }
  if (s === 'ready') {
    // Refresh cache while the key is available
    refreshEmergencyCache(ks.dataKey)
  }
  if (s === 'locked') {
    lockPin.value = ''
    lockError.value = ''
    showEmergency.value = false
    emergency.value = null
    nextTick(() => pinRef.value?.focus())
  }
})

async function submit() {
  if (!passphrase.value || busy.value) return
  busy.value = true
  error.value = ''
  try {
    await ks.submitPassphrase(passphrase.value)
    passphrase.value = ''
  } catch {
    error.value = 'Incorrect passphrase. Please try again.'
  } finally {
    busy.value = false
  }
}

// Emergency info
const EMERGENCY_CACHE_KEY = 'ks:emergency-profile'
const showEmergency = ref(false)
const emergency = ref(null)
const emergencyLoading = ref(false)
const hasAnyEmergencyData = computed(() => emergency.value && (
  emergency.value.display_name || emergency.value.legal_name || emergency.value.blood_type ||
  emergency.value.allergies || emergency.value.medical_notes || emergency.value.contacts?.length
))

async function toggleEmergency() {
  showEmergency.value = !showEmergency.value
  if (!showEmergency.value) return
  const cached = localStorage.getItem(EMERGENCY_CACHE_KEY)
  if (cached) {
    try { emergency.value = JSON.parse(cached); return } catch {}
  }
  emergencyLoading.value = true
  emergency.value = null
  emergencyLoading.value = false
}

// Lock PIN flow
const lockPin = ref('')
const unlocking = ref(false)
const lockError = ref('')
const pinRef = ref(null)

async function submitUnlock() {
  if (unlocking.value) return
  if (ks.lockConfigured && !lockPin.value) return
  unlocking.value = true
  lockError.value = ''
  try {
    await ks.unlock(lockPin.value || undefined)
    lockPin.value = ''
  } catch {
    lockError.value = 'Incorrect PIN. Please try again.'
    nextTick(() => pinRef.value?.focus())
  } finally {
    unlocking.value = false
  }
}
</script>
