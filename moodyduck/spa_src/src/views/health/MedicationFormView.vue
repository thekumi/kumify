<template>
    <div class="pb-nav">
        <TopBar :title="id ? 'Edit Medication' : 'New Medication'" :back="true" />
        <form @submit.prevent="save" class="px-4 py-4 space-y-3">
            <!-- Basic info -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
                    <input v-model="form.name"
                           type="text"
                           placeholder="e.g. Ibuprofen 400mg"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Icon</label>
                    <div class="flex gap-2 flex-wrap">
                        <button v-for="opt in ICONS"
                                :key="opt.cls"
                                type="button"
                                @click="form.icon = opt.cls"
                                :class="form.icon === opt.cls
                                    ? 'bg-blue-100 border-blue-400 text-blue-700'
                                    : 'bg-stone-50 border-stone-200 text-stone-500 hover:bg-stone-100'"
                                class="w-10 h-10 rounded-xl border flex items-center justify-center transition-colors">
                            <i :class="opt.cls" class="text-xl"></i>
                        </button>
                    </div>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Dosage per intake</label>
                    <input v-model="form.dosage"
                           type="text"
                           placeholder="e.g. 1 tablet, 400 mg"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Current supply</label>
                    <input v-model.number="form.supply"
                           type="number"
                           step="0.5"
                           min="0"
                           placeholder="e.g. 30"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Notes</label>
                    <textarea v-model="form.notes"
                              rows="2"
                              placeholder="Instructions, side effects, prescriber…"
                              class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
                </div>
                <label class="flex items-center gap-3 cursor-pointer">
                    <button type="button"
                            @click="form.prn = !form.prn"
                            class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                            :class="form.prn ? 'bg-blue-600' : 'bg-stone-200'">
                        <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                              :class="form.prn ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                    <span class="text-sm text-stone-700 font-medium">As needed (PRN)</span>
                </label>
            </div>
            <!-- Schedule -->
            <div v-if="!form.prn"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <p class="text-sm font-semibold text-stone-700">Schedule</p>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Start date</label>
                    <input v-model="form.start"
                           type="date"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <!-- Times of day -->
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Times</label>
                    <div class="space-y-2">
                        <div v-for="(t, i) in form.times" :key="i" class="flex items-center gap-2">
                            <input :value="t"
                                   @change="updateTime(i, $event.target.value)"
                                   type="time"
                                   class="flex-1 text-sm text-stone-700 border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-400" />
                            <button type="button"
                                    @click="removeTime(i)"
                                    :disabled="form.times.length <= 1"
                                    class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-red-50 text-stone-300 hover:text-red-400 transition-colors disabled:opacity-30 shrink-0">
                                <i class="ph ph-minus-circle text-lg"></i>
                            </button>
                        </div>
                    </div>
                    <button type="button"
                            @click="addTime"
                            class="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors mt-2">
                        <i class="ph ph-plus-circle"></i> Add time
                    </button>
                </div>
                <!-- Recurrence -->
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-2">Repeats</label>
                    <div class="flex gap-2 flex-wrap mb-3">
                        <button v-for="f in FREQS"
                                :key="f.val"
                                type="button"
                                @click="form.freq = f.val; if (f.val !== 'WEEKLY') form.bydays = []"
                                :class="form.freq === f.val
                                    ? 'bg-blue-100 border-blue-400 text-blue-700'
                                    : 'bg-stone-50 border-stone-200 text-stone-500 hover:bg-stone-100'"
                                class="px-3 py-1 rounded-lg border text-sm font-medium transition-colors">
                            {{ f.label }}
                        </button>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-sm text-stone-500 shrink-0">Every</span>
                        <input v-model.number="form.interval"
                               type="number"
                               min="1"
                               max="365"
                               class="w-16 text-sm text-stone-700 border border-stone-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-400 text-center" />
                        <span class="text-sm text-stone-500">{{ freqUnit }}</span>
                    </div>
                    <div v-if="form.freq === 'WEEKLY'" class="flex gap-1.5 mt-3">
                        <button v-for="d in DAYS"
                                :key="d.val"
                                type="button"
                                @click="toggleDay(d.val)"
                                :class="form.bydays.includes(d.val)
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-stone-100 text-stone-600 hover:bg-stone-200'"
                                class="w-9 h-9 rounded-full text-xs font-semibold transition-colors shrink-0">
                            {{ d.label }}
                        </button>
                    </div>
                </div>
                <!-- End condition -->
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-2">Ends</label>
                    <div class="flex gap-2 flex-wrap mb-2">
                        <button v-for="e in END_TYPES"
                                :key="e.val"
                                type="button"
                                @click="form.end_type = e.val"
                                :class="form.end_type === e.val
                                    ? 'bg-blue-100 border-blue-400 text-blue-700'
                                    : 'bg-stone-50 border-stone-200 text-stone-500 hover:bg-stone-100'"
                                class="px-3 py-1 rounded-lg border text-sm font-medium transition-colors">
                            {{ e.label }}
                        </button>
                    </div>
                    <input v-if="form.end_type === 'until'"
                           v-model="form.until"
                           type="date"
                           class="w-full px-3 py-2 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
                    <div v-if="form.end_type === 'count'" class="flex items-center gap-2">
                        <span class="text-sm text-stone-500">After</span>
                        <input v-model.number="form.count"
                               type="number"
                               min="1"
                               class="w-20 text-sm text-stone-700 border border-stone-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-400 text-center" />
                        <span class="text-sm text-stone-500">dose(s)</span>
                    </div>
                </div>
                <!-- Reminder -->
                <label class="flex items-center gap-3 cursor-pointer">
                    <button type="button"
                            @click="form.reminder = !form.reminder"
                            class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                            :class="form.reminder ? 'bg-blue-600' : 'bg-stone-200'">
                        <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                              :class="form.reminder ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                    <span class="text-sm text-stone-700 font-medium">Remind me at scheduled times</span>
                </label>
            </div>
            <p v-if="error"
               class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>
            <button type="submit"
                    :disabled="saving"
                    class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
                {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add medication') }}
            </button>
            <button v-if="id"
                    type="button"
                    @click="remove"
                    class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                Delete medication
            </button>
        </form>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { createOrQueue, updateOrQueue, deleteOrQueue } from '@/lib/offlineMutation'
import { dbGetAll } from '@/lib/db'

const ICONS = [
  { cls: 'ph ph-pill' },
  { cls: 'ph ph-eyedrop' },
  { cls: 'ph ph-syringe' },
  { cls: 'ph ph-heart-pulse' },
  { cls: 'ph ph-drop' },
  { cls: 'ph ph-flask' },
]
const FREQS = [
  { val: 'DAILY', label: 'Daily' },
  { val: 'WEEKLY', label: 'Weekly' },
  { val: 'MONTHLY', label: 'Monthly' },
  { val: 'YEARLY', label: 'Yearly' },
]
const DAYS = [
  { val: 'MO', label: 'Mo' },
  { val: 'TU', label: 'Tu' },
  { val: 'WE', label: 'We' },
  { val: 'TH', label: 'Th' },
  { val: 'FR', label: 'Fr' },
  { val: 'SA', label: 'Sa' },
  { val: 'SU', label: 'Su' },
]
const END_TYPES = [
  { val: 'none', label: 'Never' },
  { val: 'until', label: 'On date' },
  { val: 'count', label: 'After N doses' },
]

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id

const today = new Date().toISOString().slice(0, 10)
const form = ref({
  name: '',
  icon: 'ph ph-pill',
  dosage: '',
  supply: null,
  prn: false,
  notes: '',
  reminder: false,
  start: today,
  times: ['08:00'],
  freq: 'DAILY',
  interval: 1,
  bydays: [],
  end_type: 'none',
  until: '',
  count: null,
})
const saving = ref(false)
const error = ref('')
let rawMedication = null

const freqUnit = computed(() => {
  const map = { DAILY: 'day(s)', WEEKLY: 'week(s)', MONTHLY: 'month(s)', YEARLY: 'year(s)' }
  return map[form.value.freq] || ''
})

function addTime() {
  form.value.times = [...form.value.times, '12:00']
}
function removeTime(i) {
  if (form.value.times.length <= 1) return
  form.value.times = form.value.times.filter((_, idx) => idx !== i)
}
function updateTime(i, value) {
  const times = [...form.value.times]
  times[i] = value
  form.value.times = times
}
function toggleDay(d) {
  if (form.value.bydays.includes(d)) {
    form.value.bydays = form.value.bydays.filter(x => x !== d)
  } else {
    form.value.bydays = [...form.value.bydays, d]
  }
}

function buildRRule() {
  if (form.value.prn) return null
  const parts = [`FREQ=${form.value.freq}`]
  if (form.value.interval > 1) parts.push(`INTERVAL=${form.value.interval}`)
  if (form.value.freq === 'WEEKLY' && form.value.bydays.length) {
    parts.push(`BYDAY=${form.value.bydays.join(',')}`)
  }
  if (form.value.end_type === 'until' && form.value.until) {
    parts.push(`UNTIL=${form.value.until.replace(/-/g, '')}`)
  } else if (form.value.end_type === 'count' && form.value.count > 0) {
    parts.push(`COUNT=${form.value.count}`)
  }
  return parts.join(';')
}

function buildPayload() {
  const p = {
    name: form.value.name || null,
    icon: form.value.icon || 'ph ph-pill',
    dosage: form.value.dosage || null,
    supply: form.value.supply ?? null,
    prn: form.value.prn,
    notes: form.value.notes || null,
    reminder: form.value.reminder,
  }
  if (!form.value.prn) {
    p.start = form.value.start || null
    p.times = form.value.times.filter(Boolean)
    p.rrule = buildRRule()
  }
  return p
}

function fillFromDecrypted(dec) {
  form.value.name = dec.name ?? ''
  form.value.icon = dec.icon ?? 'ph ph-pill'
  form.value.dosage = dec.dosage ?? ''
  form.value.supply = dec.supply ?? null
  form.value.prn = dec.prn ?? false
  form.value.notes = dec.notes ?? ''
  form.value.reminder = dec.reminder ?? false
  form.value.start = dec.start ?? today
  form.value.times = dec.times?.length ? dec.times : ['08:00']
  if (dec.rrule) {
    const r = Object.fromEntries(dec.rrule.split(';').map(p => p.split('=')))
    form.value.freq = r.FREQ ?? 'DAILY'
    form.value.interval = r.INTERVAL ? +r.INTERVAL : 1
    form.value.bydays = r.BYDAY ? r.BYDAY.split(',') : []
    if (r.UNTIL) {
      form.value.end_type = 'until'
      const u = r.UNTIL
      form.value.until = u.length >= 8 ? `${u.slice(0,4)}-${u.slice(4,6)}-${u.slice(6,8)}` : u
    } else if (r.COUNT) {
      form.value.end_type = 'count'
      form.value.count = +r.COUNT
    } else {
      form.value.end_type = 'none'
    }
  }
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload = buildPayload()
    const encrypted_payload = await ks.encryptPayload(payload)
    if (id) {
      await updateOrQueue('/health/medications/', id, { encrypted_payload }, 'medications', rawMedication)
    } else {
      await createOrQueue('/health/medications/', { encrypted_payload }, 'medications')
    }
    router.push('/health/medications')
  } catch {
    error.value = 'Could not save.'
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!confirm('Delete this medication?')) return
  await deleteOrQueue('/health/medications/', id, 'medications')
  router.push('/health/medications')
}

onMounted(async () => {
  if (id) {
    const all = await dbGetAll('medications')
    rawMedication = all.find(m => String(m.id) === String(id)) ?? null
    if (rawMedication) {
      const dec = await ks.decrypt(rawMedication)
      fillFromDecrypted(dec)
    }
  }
})
</script>
