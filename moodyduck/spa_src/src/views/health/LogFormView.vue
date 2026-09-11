<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Log' : 'New Health Log'" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Notes <span class="font-normal">(optional)</span></label>
          <textarea v-model="form.notes" rows="3" placeholder="Any notes about this check-in…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>

        <div v-if="parameters.length">
          <p class="text-sm font-semibold text-stone-500 mb-2">Measurements</p>
          <div class="space-y-2">
            <div v-for="p in parameters" :key="p.id" class="flex items-center gap-3">
              <div class="flex-1">
                <label class="text-sm text-stone-700">{{ p.name }}</label>
              </div>
              <div class="flex items-center gap-1.5">
                <input
                  v-model.number="records[p.id]"
                  type="number"
                  step="any"
                  :placeholder="`0 ${p.unit}`"
                  class="w-24 px-2.5 py-2 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-green-400 text-stone-800 bg-stone-50 text-sm text-right"
                />
                <span class="text-xs text-stone-400 w-8 shrink-0">{{ p.unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!parameters.length" class="text-sm text-stone-400 text-center py-2">
          No health parameters defined.
          <RouterLink to="/health/parameters" class="text-green-600 underline">Manage parameters</RouterLink>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Save log') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete log
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
import { getLog, createLog, updateLog, deleteLog, getParameters } from '@/api/health'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ notes: '' })
const parameters = ref([])
const records = ref({})
const loading = ref(true)
const saving = ref(false)
const error = ref('')
let rawLog = null

async function fillNotes(l) {
  const dec = await ks.decrypt(l)
  form.value.notes = dec.notes ?? ''
}

watch(() => ks.dataKey, async (key) => { if (key && rawLog) await fillNotes(rawLog) })

async function save() {
  saving.value = true; error.value = ''
  try {
    const payload = {
      notes: form.value.notes || null,
      records: Object.entries(records.value)
        .filter(([, v]) => v !== null && v !== '' && v !== undefined)
        .map(([parameter, value]) => ({ parameter: Number(parameter), value })),
    }
    if (id) await saveEncrypted(updateLog, id, payload, ['notes'], rawLog, ks)
    else await createLog(payload)
    router.push('/health/logs')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this log?')) return
  await deleteLog(id)
  router.push('/health/logs')
}

onMounted(async () => {
  parameters.value = await getParameters()
  if (id) {
    rawLog = await getLog(id)
    await fillNotes(rawLog)
    for (const r of rawLog.records ?? []) {
      records.value[r.parameter.id] = r.value
    }
  }
  loading.value = false
})
</script>
