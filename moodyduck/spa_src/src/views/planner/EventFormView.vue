<template>
    <div class="pb-nav">
        <TopBar :title="id ? 'Edit Event' : 'New Event'" :back="true" />
        <form @submit.prevent="save" class="px-4 py-4 space-y-3">
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Title <span class="text-red-400">*</span></label>
                    <input v-model="form.title"
                           type="text"
                           required
                           placeholder="Event title"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Calendar</label>
                    <select v-model="form.calendar"
                            required
                            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm">
                        <option v-for="cal in userCalendars"
                                :key="cal.id"
                                :value="cal.id">{{ cal.name || '(unnamed calendar)' }}</option>
                    </select>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                    <input v-model="form.all_day"
                           type="checkbox"
                           class="w-4 h-4 rounded accent-violet-600" />
                    <span class="text-sm text-stone-700 font-medium">All day</span>
                </label>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="text-sm font-semibold text-stone-500 block mb-1.5">Start <span class="text-red-400">*</span></label>
                        <input v-model="form.start"
                               :type="form.all_day ? 'date' : 'datetime-local'"
                               required
                               class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                    </div>
                    <div>
                        <label class="text-sm font-semibold text-stone-500 block mb-1.5">End</label>
                        <input v-model="form.end"
                               :type="form.all_day ? 'date' : 'datetime-local'"
                               class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                    </div>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Repeat</label>
                    <select v-model="form.recurrence"
                            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm">
                        <option value="">Does not repeat</option>
                        <option value="DAILY">Daily</option>
                        <option value="WEEKLY">Weekly</option>
                        <option value="MONTHLY">Monthly</option>
                        <option value="YEARLY">Yearly</option>
                    </select>
                    <div v-if="form.recurrence === 'WEEKLY'"
                         class="flex flex-wrap gap-1.5 mt-2">
                        <label v-for="d in DOW_OPTIONS"
                               :key="d.code"
                               class="flex items-center gap-1 cursor-pointer">
                            <input type="checkbox"
                                   :value="d.code"
                                   v-model="form.weekDays"
                                   class="sr-only" />
                            <span class="w-8 h-8 flex items-center justify-center rounded-full text-xs font-semibold transition-colors"
                                  :class="form.weekDays.includes(d.code)
                                      ? 'bg-violet-600 text-white'
                                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'">{{ d.short }}</span>
                        </label>
                    </div>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Notes</label>
                    <textarea v-model="form.notes"
                              rows="3"
                              placeholder="Optional notes…"
                              class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
                </div>
            </div>
            <p v-if="error"
               class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>
            <button type="submit"
                    :disabled="saving || !form.calendar"
                    class="w-full py-3.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
                {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add event') }}
            </button>
            <button v-if="id"
                    type="button"
                    @click="remove"
                    class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                Delete event
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
import { usePlannerStore } from '@/stores/planner'
import { getEvents, createEvent, updateEvent, deleteEvent } from '@/api/planner'

const ks = useKeystoreStore()
const plannerStore = usePlannerStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id ?? null

const DOW_OPTIONS = [
  { code: 'MO', short: 'Mo' },
  { code: 'TU', short: 'Tu' },
  { code: 'WE', short: 'We' },
  { code: 'TH', short: 'Th' },
  { code: 'FR', short: 'Fr' },
  { code: 'SA', short: 'Sa' },
  { code: 'SU', short: 'Su' },
]

const form = ref({
  title: '',
  notes: '',
  calendar: '',
  all_day: false,
  start: '',
  end: '',
  recurrence: '',
  weekDays: [],
})
const saving = ref(false)
const error = ref('')
let rawEvent = null

const userCalendars = computed(() =>
  plannerStore.calendars.filter(c => !c.virtual_key)
)

watch(userCalendars, (cals) => {
  if (!form.value.calendar && cals.length) {
    form.value.calendar = cals[0].id
  }
})

watch(() => form.value.recurrence, (rec) => {
  if (rec === 'WEEKLY' && form.value.start && !form.value.weekDays.length) {
    const DAY_CODES = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']
    const d = new Date(form.value.start)
    form.value.weekDays = [DAY_CODES[d.getDay()]]
  }
})

async function fillForm(ev) {
  const dec = await ks.decrypt(ev)
  let recurrence = ''
  let weekDays = []
  if (ev.rrule) {
    const parts = Object.fromEntries(
      ev.rrule.split(';').map(p => {
        const eq = p.indexOf('=')
        return [p.slice(0, eq), p.slice(eq + 1)]
      })
    )
    recurrence = parts.FREQ || ''
    if (recurrence === 'WEEKLY' && parts.BYDAY) {
      weekDays = parts.BYDAY.split(',')
    }
  }
  form.value = {
    title: dec.title ?? '',
    notes: dec.notes ?? '',
    calendar: ev.calendar,
    all_day: ev.all_day ?? false,
    start: toInputValue(ev.start, ev.all_day),
    end: ev.end ? toInputValue(ev.end, ev.all_day) : '',
    recurrence,
    weekDays,
  }
}

function toInputValue(iso, allDay) {
  if (!iso) return ''
  if (allDay) return iso.slice(0, 10)
  const d = new Date(iso)
  return d.toISOString().slice(0, 16)
}

function buildRRule() {
  if (!form.value.recurrence) return null
  if (form.value.recurrence === 'WEEKLY') {
    const days = form.value.weekDays.length > 0 ? form.value.weekDays : ['MO']
    return `FREQ=WEEKLY;BYDAY=${days.join(',')}`
  }
  return `FREQ=${form.value.recurrence}`
}

watch(() => ks.dataKey, async (key) => {
  if (key) {
    if (!plannerStore.loaded) await plannerStore.load(ks)
    if (!form.value.calendar && userCalendars.value.length) {
      form.value.calendar = userCalendars.value[0].id
    }
    if (id && rawEvent) await fillForm(rawEvent)
  }
})

onMounted(async () => {
  if (!plannerStore.loaded && ks.dataKey) await plannerStore.load(ks)
  if (userCalendars.value.length) form.value.calendar = userCalendars.value[0].id

  if (id) {
    const events = await getEvents()
    rawEvent = events.find(e => e.id === id)
    if (rawEvent && ks.dataKey) await fillForm(rawEvent)
  }
})

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload = { title: form.value.title }
    if (form.value.notes) payload.notes = form.value.notes
    const encrypted_payload = await ks.encryptPayload(payload)

    const start = form.value.all_day
      ? form.value.start
      : new Date(form.value.start).toISOString()
    const end = form.value.end
      ? (form.value.all_day ? form.value.end : new Date(form.value.end).toISOString())
      : null

    const body = {
      calendar: form.value.calendar,
      all_day: form.value.all_day,
      start,
      end,
      encrypted_payload,
      rrule: buildRRule(),
    }

    if (id) {
      await updateEvent(id, body)
    } else {
      await createEvent(body)
    }
    router.push('/planner')
  } catch (e) {
    error.value = e?.data?.detail ?? 'Failed to save event.'
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!confirm('Delete this event?')) return
  await deleteEvent(id)
  router.push('/planner')
}
</script>
