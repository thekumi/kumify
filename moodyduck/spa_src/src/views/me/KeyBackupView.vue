<template>
  <div class="pb-nav">
    <TopBar title="Key Backup" :back="true" />

    <div class="px-4 py-4 space-y-4">
      <!-- Status card -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
               :class="existing ? 'bg-green-100' : 'bg-amber-100'">
            <i :class="existing ? 'ph ph-shield-check text-green-600' : 'ph ph-shield-warning text-amber-600'"
               class="text-xl"></i>
          </div>
          <div>
            <p class="font-semibold text-stone-800">
              {{ existing ? 'Backup passphrase set' : 'No backup passphrase' }}
            </p>
            <p class="text-sm text-stone-400 mt-0.5">
              <template v-if="existing">
                Last updated {{ fmtDate(existing.updated_at) }}.
                If you lose access to all your devices, you can recover your encryption key with this passphrase.
              </template>
              <template v-else>
                Without a backup, losing access to all your devices means losing all encrypted data permanently.
              </template>
            </p>
          </div>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center py-8">
        <div class="w-7 h-7 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
      </div>

      <!-- No data key yet -->
      <div v-else-if="!ks.dataKey" class="bg-amber-50 rounded-2xl border border-amber-100 p-4">
        <p class="text-sm text-amber-700">
          <i class="ph ph-warning mr-1"></i>
          Encryption key not yet loaded. Wait for the keystore to finish booting, then return here.
        </p>
      </div>

      <!-- Set / update form -->
      <form v-else @submit.prevent="save" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <p class="text-sm font-semibold text-stone-500">
          {{ existing ? 'Update backup passphrase' : 'Set a backup passphrase' }}
        </p>

        <div>
          <label class="text-sm font-medium text-stone-500 block mb-1.5">Passphrase</label>
          <input v-model="form.passphrase" type="password" required minlength="12"
            placeholder="At least 12 characters"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>

        <div>
          <label class="text-sm font-medium text-stone-500 block mb-1.5">Confirm passphrase</label>
          <input v-model="form.confirm" type="password" required
            placeholder="Repeat passphrase"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>

        <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ error }}</p>
        <p v-if="success" class="text-sm text-green-700 bg-green-50 rounded-xl px-3 py-2">{{ success }}</p>

        <button type="submit" :disabled="saving"
          class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
          {{ saving ? 'Saving…' : (existing ? 'Update backup' : 'Create backup') }}
        </button>
      </form>

      <!-- Info box -->
      <div class="bg-stone-50 rounded-2xl border border-stone-100 p-4">
        <p class="text-xs text-stone-400 leading-relaxed">
          Your encryption key is wrapped with PBKDF2 + AES-GCM and stored on the server.
          The server never sees your passphrase or your unencrypted key.
          Choose a strong, memorable passphrase — there is no recovery if you forget it.
        </p>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { wrapDataKeyForBackup } from '@/keystore/backup'
import { apiFetch } from '@/keystore/util'

const ks = useKeystoreStore()
const existing = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ passphrase: '', confirm: '' })

const fmtDate = (d) => new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })

async function save() {
  error.value = ''; success.value = ''
  if (form.value.passphrase !== form.value.confirm) {
    error.value = 'Passphrases do not match.'
    return
  }
  if (form.value.passphrase.length < 12) {
    error.value = 'Passphrase must be at least 12 characters.'
    return
  }
  saving.value = true
  try {
    const payload = await wrapDataKeyForBackup(ks.dataKey, form.value.passphrase)
    const res = await apiFetch('POST', '/api/keybackup/', payload)
    if (!res.ok) throw new Error()
    existing.value = await res.json()
    form.value = { passphrase: '', confirm: '' }
    success.value = 'Backup saved successfully.'
  } catch {
    error.value = 'Could not save backup. Please try again.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const res = await apiFetch('GET', '/api/keybackup/')
  if (res.ok) existing.value = await res.json()
  loading.value = false
})
</script>
