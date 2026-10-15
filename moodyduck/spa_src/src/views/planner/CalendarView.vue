<template>
    <div class="pb-nav">
        <TopBar title="Planner">
        <template #actions>
            <RouterLink to="/planner/settings" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
            <i class="ph ph-gear text-stone-500"></i>
            </RouterLink>
            <RouterLink v-if="activeTab === 'calendar'" to="/planner/events/new" class="w-8 h-8 flex items-center justify-center rounded-full bg-violet-100 hover:bg-violet-200 transition-colors">
            <i class="ph ph-plus text-violet-700"></i>
            </RouterLink>
            <button v-else-if="activeTab === 'tasks'"
                    @click="tasksPanelRef?.triggerAddTask()"
                    class="w-8 h-8 flex items-center justify-center rounded-full bg-violet-100 hover:bg-violet-200 transition-colors">
                <i class="ph ph-plus text-violet-700"></i>
            </button>
        </template>
        </TopBar>
        <div class="flex gap-0 border-b border-stone-100">
            <button @click="activeTab = 'calendar'"
                    class="flex-1 py-3 text-sm font-semibold transition-colors"
                    :class="activeTab === 'calendar' ? 'text-violet-700 border-b-2 border-violet-600' : 'text-stone-400'">
                <i class="ph ph-calendar mr-1"></i>Calendar
            </button>
            <button @click="activeTab = 'tasks'"
                    class="flex-1 py-3 text-sm font-semibold transition-colors"
                    :class="activeTab === 'tasks' ? 'text-violet-700 border-b-2 border-violet-600' : 'text-stone-400'">
                <i class="ph ph-check-square mr-1"></i>Tasks
            </button>
        </div>
        <div v-if="activeTab === 'calendar'">
            <div class="flex items-center justify-between px-4 py-3">
                <button @click="prevMonth"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
                    <i class="ph ph-caret-left text-stone-600"></i>
                </button>
                <span class="font-semibold text-stone-800">{{ monthLabel }}</span>
                <button @click="nextMonth"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
                    <i class="ph ph-caret-right text-stone-600"></i>
                </button>
            </div>
            <div class="grid grid-cols-7 px-2 mb-1">
                <div v-for="d in weekDays"
                     :key="d"
                     class="text-center text-xs font-semibold text-stone-400 py-1">{{ d }}</div>
            </div>
            <div v-if="loading" class="flex justify-center py-12">
                <div class="w-7 h-7 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
            </div>
            <div v-else class="grid grid-cols-7 px-2 gap-px">
                <button v-for="cell in monthGrid"
                        :key="cell.iso"
                        @click="selectDay(cell)"
                        class="relative flex flex-col items-center pt-1 pb-0.5 rounded-xl transition-colors min-h-[52px]"
                        :class="[
                            cell.inMonth ? 'hover:bg-stone-50' : 'opacity-30',
                            cell.iso === selectedDay ? 'bg-violet-50' : '',
                            cell.iso === todayIso ? 'font-bold' : '',
                        ]">
                    <span class="text-xs w-6 h-6 flex items-center justify-center rounded-full"
                          :class="cell.iso === todayIso ? 'bg-violet-600 text-white' : 'text-stone-700'">
                        {{ cell.day }}
                    </span>
                    <div class="flex flex-wrap gap-px justify-center mt-0.5 max-w-full px-0.5">
                        <span v-for="ev in (dayEvents[cell.iso] || []).slice(0, 3)"
                              :key="ev.id"
                              class="w-1.5 h-1.5 rounded-full"
                              :style="{ background: calendarColor(ev) }"></span>
                        <span v-if="(dayEvents[cell.iso] || []).length > 3"
                              class="text-[9px] text-stone-400 leading-none">
                            +{{ (dayEvents[cell.iso] || []).length - 3 }}
                        </span>
                    </div>
                </button>
            </div>
            <div v-if="selectedDay"
                 class="mx-4 mt-4 bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden">
                <div class="px-4 py-3 border-b border-stone-50 flex items-center justify-between">
                    <span class="font-semibold text-stone-800 text-sm">{{ selectedDayLabel }}</span>
                    <button @click="selectedDay = null"
                            class="text-stone-300 hover:text-stone-500">
                        <i class="ph ph-x"></i>
                    </button>
                </div>
                <div v-if="!(dayEvents[selectedDay] || []).length"
                     class="px-4 py-5 text-sm text-stone-400 text-center">No events</div>
                <ul v-else class="divide-y divide-stone-50">
                    <component :is="ev.virtual ? 'li' : 'RouterLink'" v-for="ev in dayEvents[selectedDay]" :key="ev.id" :to="ev.virtual ? undefined : `/planner/events/${ev.id.split(':')[0]}`" class="flex items-center gap-3 px-4 py-3 hover:bg-stone-50 transition-colors" :class="ev.virtual ? '' : 'cursor-pointer'">
                    <span class="w-2.5 h-2.5 rounded-full shrink-0"
                          :style="{ background: calendarColor(ev) }"></span>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-stone-800 truncate">{{ ev.title || ev.encrypted_payload?.title || '(no title)' }}</p>
                        <p v-if="!ev.all_day" class="text-xs text-stone-400">{{ formatTime(ev.start) }}</p>
                    </div>
                    <span v-if="ev.virtual" class="text-xs text-stone-300 italic shrink-0">auto</span>
                    <i v-else class="ph ph-caret-right text-stone-300 shrink-0"></i>
                    </component>
                </ul>
            </div>
        </div>
        <TasksPanel v-else ref="tasksPanelRef" :calendars="plannerStore.calendars" :task-lists="plannerStore.taskLists" />
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import TasksPanel from './TasksPanel.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { usePlannerStore } from '@/stores/planner'
import { getEvents } from '@/api/planner'
import { getCalendarProvider } from '@/planner/registry'
import { expandRRule } from '@/planner/rrule'
import { syncCalendarsToSystem } from '@/planner/calendarSync'

const ks = useKeystoreStore()
const plannerStore = usePlannerStore()

const activeTab = ref('calendar')
const loading = ref(true)
const selectedDay = ref(null)
const tasksPanelRef = ref(null)

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth())

const todayIso = new Date().toISOString().slice(0, 10)
const weekDays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']

const monthLabel = computed(() => `${MONTH_NAMES[month.value]} ${year.value}`)

const monthGrid = computed(() => {
  const firstDay = new Date(year.value, month.value, 1)
  const startOffset = (firstDay.getDay() + 6) % 7
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(year.value, month.value, 1 + i - startOffset)
    return {
      iso: d.toISOString().slice(0, 10),
      day: d.getDate(),
      inMonth: d.getMonth() === month.value,
    }
  })
})

const rangeStart = computed(() => monthGrid.value[0].iso)
const rangeEnd = computed(() => monthGrid.value[41].iso)

const allEvents = ref([])
const dayEvents = computed(() => {
  const map = {}
  const visibleIds = new Set(
    plannerStore.calendars.filter(c => c.is_visible).map(c => c.id)
  )
  const visibleKeys = new Set(
    plannerStore.calendars.filter(c => c.is_visible && c.virtual_key).map(c => c.virtual_key)
  )
  for (const ev of allEvents.value) {
    if (ev.virtual) {
      if (!visibleKeys.has(ev.virtual_key)) continue
    } else {
      if (!visibleIds.has(ev.calendar)) continue
    }
    const day = ev.start.slice(0, 10)
    if (!map[day]) map[day] = []
    map[day].push(ev)
  }
  return map
})

const calendarMap = computed(() => Object.fromEntries(plannerStore.calendars.map(c => [c.id, c])))

function calendarColor(ev) {
  if (ev.virtual) {
    const cal = plannerStore.calendars.find(c => c.virtual_key === ev.virtual_key)
    return cal?.color ?? '#6366F1'
  }
  return calendarMap.value[ev.calendar]?.color ?? '#6366F1'
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const selectedDayLabel = computed(() => {
  if (!selectedDay.value) return ''
  const d = new Date(selectedDay.value + 'T00:00:00')
  return d.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })
})

function selectDay(cell) {
  selectedDay.value = selectedDay.value === cell.iso ? null : cell.iso
}

function prevMonth() {
  if (month.value === 0) { month.value = 11; year.value-- }
  else month.value--
}

function nextMonth() {
  if (month.value === 11) { month.value = 0; year.value++ }
  else month.value++
}

async function loadEvents() {
  if (!ks.dataKey) return
  loading.value = true
  allEvents.value = []

  const from = rangeStart.value
  const to = rangeEnd.value

  try {
    const [rawEvents, ...virtualResults] = await Promise.all([
      getEvents({ from, to }),
      ...plannerStore.calendars
        .filter(c => c.virtual_key)
        .map(c => {
          const fn = getCalendarProvider(c.virtual_key)
          return fn ? fn(ks, from, to).catch(() => []) : Promise.resolve([])
        }),
    ])
    const decrypted = await ks.decryptAll(rawEvents)
    const expanded = decrypted.flatMap(ev => ev.rrule ? expandRRule(ev, from, to) : [ev])
    allEvents.value = [...expanded, ...virtualResults.flat()]
  } finally {
    loading.value = false
  }
}

watch([year, month], loadEvents)
watch(() => ks.dataKey, async (key) => {
  if (key) {
    if (!plannerStore.loaded) await plannerStore.load(ks)
    await loadEvents()
  }
})

onMounted(async () => {
  if (ks.dataKey) {
    if (!plannerStore.loaded) await plannerStore.load(ks)
    await loadEvents()
    syncCalendarsToSystem(ks, plannerStore).catch(() => {})
  }
})
</script>
