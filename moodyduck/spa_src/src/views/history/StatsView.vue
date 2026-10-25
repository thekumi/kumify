<template>
    <div class="pb-nav">
        <TopBar title="Statistics" :back="true" />
        <div v-if="loading"
             class="flex flex-col items-center justify-center py-20 gap-3">
            <div class="w-8 h-8 border-4 border-stone-200 border-t-violet-500 rounded-full animate-spin"></div>
            <p class="text-sm text-stone-400">Loading your data…</p>
        </div>
        <div v-else class="px-4 py-4 space-y-4">
            <!-- Global range selector -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-1 flex">
                <button type="button"
                        v-for="d in [7, 30, 90, 0]"
                        :key="d"
                        @click="isCustom = false; yearMode = false; rangeDays = d"
                        class="flex-1 text-xs py-2 rounded-xl font-medium transition-colors"
                        :class="!isCustom && !yearMode && rangeDays === d ? 'bg-violet-100 text-violet-700' : 'text-stone-400 hover:text-stone-600'">
                    {{ d === 0 ? 'All' : d + 'd' }}
                </button>
                <button type="button"
                        @click="isCustom = false; yearMode = true"
                        class="flex-1 text-xs py-2 rounded-xl font-medium transition-colors"
                        :class="yearMode ? 'bg-violet-100 text-violet-700' : 'text-stone-400 hover:text-stone-600'">
                    Year
                </button>
                <button type="button"
                        @click="isCustom = true; yearMode = false"
                        class="flex-1 text-xs py-2 rounded-xl font-medium transition-colors"
                        :class="isCustom ? 'bg-violet-100 text-violet-700' : 'text-stone-400 hover:text-stone-600'">
                    Custom
                </button>
            </div>
            <!-- Custom date range picker -->
            <div v-if="isCustom"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm px-3 py-2.5 flex items-center gap-2">
                <input v-model="customFrom"
                       type="date"
                       class="flex-1 text-sm text-stone-700 border border-stone-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-violet-400 bg-stone-50" />
                <span class="text-xs text-stone-400 shrink-0">to</span>
                <input v-model="customTo"
                       type="date"
                       class="flex-1 text-sm text-stone-700 border border-stone-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-violet-400 bg-stone-50" />
            </div>
            <!-- Year navigation -->
            <div v-if="yearMode"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm px-3 py-2 flex items-center gap-2">
                <button type="button"
                        @click="selectedYear--"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
                    <i class="ph ph-caret-left text-stone-500 text-lg"></i>
                </button>
                <span class="flex-1 text-center text-sm font-medium text-stone-700">{{ selectedYear }}</span>
                <button type="button"
                        @click="selectedYear++"
                        :disabled="selectedYear >= currentYear"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors disabled:opacity-30 shrink-0">
                    <i class="ph ph-caret-right text-stone-500 text-lg"></i>
                </button>
            </div>
            <!-- Time navigation -->
            <div v-else-if="rangeDays && !isCustom"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm px-3 py-2 flex items-center gap-2">
                <button type="button"
                        @click="goBack"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
                    <i class="ph ph-caret-left text-stone-500 text-lg"></i>
                </button>
                <span class="flex-1 text-center text-sm font-medium text-stone-700">{{ rangeLabel }}</span>
                <button type="button"
                        @click="goForward"
                        :disabled="!rangeEnd"
                        class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors disabled:opacity-30 shrink-0">
                    <i class="ph ph-caret-right text-stone-500 text-lg"></i>
                </button>
            </div>
            <!-- Summary chips -->
            <div class="grid grid-cols-2 gap-2">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ totalEntries }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Entries</p>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ totalDreams }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Dreams</p>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ activeDays }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Active days</p>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ streak }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Day streak</p>
                </div>
            </div>
            <!-- By month (year mode) -->
            <template v-if="yearMode && totalEntries > 0">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">By month</p>
                <div v-if="moodByMonthRaw.some(v => v != null)"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <p class="text-sm font-semibold text-stone-700 mb-3">Avg mood</p>
                    <div class="h-44">
                        <Bar :data="moodByMonthData" :options="moodMonthOptions" />
                    </div>
                </div>
                <div v-if="activitiesByMonthRaw.length"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <p class="text-sm font-semibold text-stone-700 mb-3">Activities</p>
                    <div class="h-64">
                        <Bar :data="activitiesByMonthData" :options="stackedBarOptions" />
                    </div>
                </div>
            </template>
            <!-- Calendar heatmap -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                <div class="flex items-center justify-between mb-3">
                    <p class="text-sm font-semibold text-stone-700">Calendar <span class="text-xs font-normal text-stone-400">{{ yearMode ? selectedYear : 'past year' }}</span></p>
                    <div class="flex gap-0.5 bg-stone-100 rounded-lg p-0.5">
                        <button type="button"
                                @click="calMode = 'activity'"
                                class="text-xs px-2.5 py-1 rounded-md transition-colors font-medium"
                                :class="calMode === 'activity' ? 'bg-white shadow-sm text-stone-700' : 'text-stone-400'">Activity</button>
                        <button type="button"
                                @click="calMode = 'mood'"
                                class="text-xs px-2.5 py-1 rounded-md transition-colors font-medium"
                                :class="calMode === 'mood' ? 'bg-white shadow-sm text-stone-700' : 'text-stone-400'">Mood</button>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <div class="flex gap-px min-w-max">
                        <div class="flex flex-col gap-px mr-1">
                            <div class="h-3 w-5"></div>
                            <div v-for="(label, i) in ['M','T','W','T','F','S','S']"
                                 :key="i"
                                 class="h-3 w-5 text-[9px] text-stone-300 flex items-center justify-end pr-1">{{ label }}</div>
                        </div>
                        <div v-for="(week, wi) in calendarWeeks"
                             :key="wi"
                             class="flex flex-col gap-px">
                            <div class="h-3 text-[9px] text-stone-300 text-center">{{ calendarMonthLabels[wi] ?? '' }}</div>
                            <div v-for="day in week"
                                 :key="day"
                                 :title="calDayTitle(day)"
                                 class="w-3 h-3 rounded-sm"
                                 :class="calMode === 'mood' ? calMoodClass(day) : calDayClass(day)"></div>
                        </div>
                    </div>
                </div>
                <div v-if="calMode === 'activity'" class="flex items-center gap-1.5 mt-2">
                    <span class="text-[10px] text-stone-400">Less</span>
                    <div v-for="cls in ['bg-stone-100','bg-clay-100','bg-clay-300','bg-clay-500','bg-clay-700']"
                         :key="cls"
                         :class="[cls, 'w-3 h-3 rounded-sm']"></div>
                    <span class="text-[10px] text-stone-400">More</span>
                </div>
                <div v-else class="flex items-center gap-1.5 mt-2 flex-wrap gap-y-1">
                    <span class="text-[10px] text-stone-400">No entry</span>
                    <div class="w-3 h-3 rounded-sm bg-stone-100"></div>
                    <span class="text-[10px] text-stone-400 ml-1">No mood</span>
                    <div class="w-3 h-3 rounded-sm bg-stone-200"></div>
                    <span class="text-[10px] text-stone-400 ml-1">Low → High</span>
                    <div v-for="cls in ['bg-rose-200','bg-amber-200','bg-stone-300','bg-emerald-200','bg-emerald-400']"
                         :key="cls"
                         :class="[cls, 'w-3 h-3 rounded-sm']"></div>
                </div>
            </div>
            <template v-if="moodLinePoints.length || moodDistRaw.labels.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Mood</p>
                <div v-if="moodLinePoints.length"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <p class="text-sm font-semibold text-stone-700 mb-3">Over time</p>
                    <div class="h-40">
                        <Line :data="moodLineData" :options="lineOptions" />
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div v-if="moodDistRaw.labels.length"
                         class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Mix</p>
                        <div class="h-44">
                            <Doughnut :data="moodDistData" :options="doughnutOptions" />
                        </div>
                    </div>
                    <div v-if="timeOfDayRaw.data.some(v => v > 0)"
                         class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Time of day</p>
                        <div class="h-44">
                            <Bar :data="timeOfDayChartData" :options="barOptions" />
                        </div>
                    </div>
                </div>
            </template>
            <template v-if="activityData.labels.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Activities</p>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <div class="h-52">
                        <Bar :data="activityChartData" :options="hBarOptions" />
                    </div>
                </div>
            </template>
            <template v-if="totalEntries > 0">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">By weekday</p>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Entries</p>
                        <div class="h-44">
                            <Bar :data="weekdayCountData" :options="barOptions" />
                        </div>
                    </div>
                    <div v-if="weekdayRaw.avgMoods.some(v => v != null)"
                         class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Avg mood</p>
                        <div class="h-44">
                            <Bar :data="weekdayMoodData" :options="barOptions" />
                        </div>
                    </div>
                </div>
            </template>
            <template v-if="allDreams.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Dreams</p>
                <div class="grid grid-cols-3 gap-2">
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                        <p class="text-2xl font-bold text-stone-800">{{ totalDreams }}</p>
                        <p class="text-xs text-stone-400 mt-0.5">Logged</p>
                    </div>
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                        <p class="text-2xl font-bold text-stone-800">{{ avgDreamsPerWeek }}</p>
                        <p class="text-xs text-stone-400 mt-0.5">Per week</p>
                    </div>
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                        <p class="text-2xl font-bold text-stone-800">{{ avgDreamWords }}</p>
                        <p class="text-xs text-stone-400 mt-0.5">Avg words</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div v-if="dreamFreqData.data.length > 1"
                         class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Frequency</p>
                        <div class="h-44">
                            <Bar :data="dreamFreqChartData" :options="dreamBarOptions" />
                        </div>
                    </div>
                    <div v-if="dreamMoodDistRaw.labels.length"
                         class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                        <p class="text-sm font-semibold text-stone-700 mb-3">Mood</p>
                        <div class="h-44">
                            <Doughnut :data="dreamMoodDistData" :options="doughnutOptions" />
                        </div>
                    </div>
                </div>
            </template>
            <template v-if="habitData.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Habits</p>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <div class="space-y-2.5">
                        <div v-for="h in habitData" :key="h.id" class="flex items-center gap-2">
                            <span class="text-sm text-stone-600 w-28 truncate shrink-0 flex items-center gap-1">
                                <i v-if="h.negative" class="ph ph-prohibit text-rose-400 shrink-0"></i>
                                {{ h.name }}
                            </span>
                            <div class="flex-1 bg-stone-100 rounded-full h-2">
                                <div class="h-2 rounded-full transition-all"
                                     :class="h.negative ? 'bg-rose-400' : 'bg-emerald-500'"
                                     :style="`width:${Math.min(100, h.count / h.expected * 100)}%`"></div>
                            </div>
                            <span class="text-xs text-stone-400 shrink-0 text-right w-16">{{ h.count }}/{{ h.expected }}</span>
                        </div>
                    </div>
                </div>
            </template>
            <template v-if="propertyCharts.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Custom</p>
                <div v-for="pc in propertyCharts"
                     :key="pc.id"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <p class="text-sm font-semibold text-stone-700 mb-3">{{ pc.name }}</p>
                    <div class="h-40">
                        <Line :data="pc.chartData" :options="lineOptions" />
                    </div>
                </div>
            </template>
            <p v-if="!totalEntries && !allDreams.length && !loading"
               class="text-center text-stone-400 text-sm py-8">No data yet — start tracking!</p>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Line, Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, TimeScale, PointElement, LineElement,
  ArcElement, BarElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { useSyncStore } from '@/stores/sync'
import { dbGetAll } from '@/lib/db'
import {
  filterByDays, filterByYear,
  moodOverTime, moodDistribution, activityFrequency,
  entryCountByTimeOfDay, calendarData, habitCompletionRates,
  buildCalendarWeeks, buildYearCalendar, dreamFrequency, currentStreak, propertyOverTime, weekdayStats,
  moodByMonth, activitiesByMonth,
} from '@/history/stats.js'

ChartJS.register(CategoryScale, LinearScale, TimeScale, PointElement, LineElement, ArcElement, BarElement, Title, Tooltip, Legend, Filler)

const ks = useKeystoreStore()
const syncStore = useSyncStore()
const loading = ref(true)
const rangeDays = ref(30)
const rangeEnd  = ref(null)
const isCustom  = ref(false)
const customFrom = ref('')
const customTo   = ref(new Date().toISOString().slice(0, 10))
const calMode = ref('activity')
const yearMode = ref(false)
const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)

watch(rangeDays, () => { rangeEnd.value = null })
watch(yearMode,  () => { rangeEnd.value = null })

function goBack() {
  const base = rangeEnd.value ? new Date(rangeEnd.value + 'T12:00:00') : new Date()
  base.setDate(base.getDate() - rangeDays.value)
  rangeEnd.value = base.toISOString().slice(0, 10)
}

function goForward() {
  if (!rangeEnd.value) return
  const base = new Date(rangeEnd.value + 'T12:00:00')
  base.setDate(base.getDate() + rangeDays.value)
  const todayStr = new Date().toISOString().slice(0, 10)
  rangeEnd.value = base.toISOString().slice(0, 10) >= todayStr ? null : base.toISOString().slice(0, 10)
}

const rangeLabel = computed(() => {
  const end = rangeEnd.value ? new Date(rangeEnd.value + 'T12:00:00') : new Date()
  const start = new Date(end)
  start.setDate(start.getDate() - rangeDays.value + 1)
  const fmt = (d) => d.toLocaleDateString(undefined, {
    month: 'short', day: 'numeric',
    ...(d.getFullYear() !== new Date().getFullYear() ? { year: 'numeric' } : {}),
  })
  return `${fmt(start)} – ${fmt(end)}`
})

const allStatuses = ref([])
const allDreams   = ref([])
const moodMap     = ref({})
const activityMap = ref({})
const calData     = ref({})
const calendarWeeks = computed(() =>
  yearMode.value ? buildYearCalendar(selectedYear.value) : buildCalendarWeeks(52)
)
const rawHabitLogs  = ref([])
const rawHabits     = ref([])
const allProperties = ref([])

// Calendar month labels

const calendarMonthLabels = computed(() => {
  const labels = {}
  const seen = new Set()
  for (let wi = 0; wi < calendarWeeks.value.length; wi++) {
    const m = new Date(calendarWeeks.value[wi][0]).toLocaleString('default', { month: 'short' })
    if (!seen.has(m)) { seen.add(m); labels[wi] = m }
  }
  return labels
})

// Filtered data — used as source for all chart computeds

function customFilter(items, getTs) {
  if (!customFrom.value || !customTo.value) return items
  const start = new Date(customFrom.value + 'T00:00:00')
  const end   = new Date(customTo.value   + 'T23:59:59.999')
  return items.filter(i => { const t = new Date(getTs(i)); return t >= start && t <= end })
}

const filteredStatuses = computed(() => {
  if (yearMode.value)  return filterByYear(allStatuses.value, selectedYear.value, s => s.timestamp)
  if (isCustom.value)  return customFilter(allStatuses.value, s => s.timestamp)
  return filterByDays(allStatuses.value, rangeDays.value, s => s.timestamp, rangeEnd.value)
})
const filteredDreams = computed(() => {
  if (yearMode.value)  return filterByYear(allDreams.value, selectedYear.value, d => d.timestamp)
  if (isCustom.value)  return customFilter(allDreams.value, d => d.timestamp)
  return filterByDays(allDreams.value, rangeDays.value, d => d.timestamp, rangeEnd.value)
})
const filteredHabitLogs = computed(() => {
  if (yearMode.value) return filterByYear(rawHabitLogs.value, selectedYear.value, l => l.date)
  return rawHabitLogs.value
})

// Summary

const totalEntries = computed(() => filteredStatuses.value.length)
const totalDreams  = computed(() => filteredDreams.value.length)
const activeDays   = computed(() => new Set(filteredStatuses.value.map(s => s.timestamp.slice(0, 10))).size)
const streak       = computed(() => currentStreak(allStatuses.value))

// Calendar

const maxCount = computed(() => Math.max(1, ...Object.values(calData.value).map(d => d.count)))

const moodCalValues = computed(() => Object.values(calData.value).map(d => d.avgMood).filter(v => v != null))
const moodCalMin    = computed(() => moodCalValues.value.length ? Math.min(...moodCalValues.value) : 0)
const moodCalMax    = computed(() => moodCalValues.value.length ? Math.max(...moodCalValues.value) : 1)

function calDayClass(day) {
  const d = calData.value[day]
  if (!d) return 'bg-stone-100'
  const r = d.count / maxCount.value
  if (r < 0.25) return 'bg-clay-100'
  if (r < 0.5)  return 'bg-clay-300'
  if (r < 0.75) return 'bg-clay-500'
  return 'bg-clay-700'
}

function calMoodClass(day) {
  const d = calData.value[day]
  if (!d) return 'bg-stone-100'
  if (d.avgMood == null) return 'bg-stone-200'
  const range = moodCalMax.value - moodCalMin.value
  const norm = range > 0 ? (d.avgMood - moodCalMin.value) / range : 0.5
  if (norm < 0.2) return 'bg-rose-200'
  if (norm < 0.4) return 'bg-amber-200'
  if (norm < 0.6) return 'bg-stone-300'
  if (norm < 0.8) return 'bg-emerald-200'
  return 'bg-emerald-400'
}

function calDayTitle(day) {
  const d = calData.value[day]
  if (!d) return day
  return `${day}: ${d.count} entr${d.count === 1 ? 'y' : 'ies'}${d.avgMood ? `, avg mood ${d.avgMood.toFixed(1)}` : ''}`
}

// Mood charts — all use pre-filtered data, days=0 so filterByDays inside is a no-op

const moodLinePoints = computed(() => moodOverTime(filteredStatuses.value, moodMap.value, 0, null))
const moodLineData   = computed(() => ({
  datasets: [{
    data: moodLinePoints.value,
    borderColor: '#7c3aed',
    backgroundColor: 'rgba(124,58,237,0.08)',
    tension: 0.3,
    fill: true,
    pointRadius: moodLinePoints.value.length > 60 ? 0 : 3,
    pointHoverRadius: 4,
  }],
}))

const moodDistRaw  = computed(() => moodDistribution(filteredStatuses.value, moodMap.value, 0, null))
const moodDistData = computed(() => ({
  labels: moodDistRaw.value.labels,
  datasets: [{ data: moodDistRaw.value.data, backgroundColor: moodDistRaw.value.colors, borderWidth: 0 }],
}))

const timeOfDayRaw       = computed(() => entryCountByTimeOfDay(filteredStatuses.value, 0, null))
const timeOfDayChartData = computed(() => ({
  labels: timeOfDayRaw.value.labels.map(l => l.split(' ')[0]),
  datasets: [{ data: timeOfDayRaw.value.data, backgroundColor: '#7c3aed66', borderRadius: 4 }],
}))

// Activity charts

const activityData      = computed(() => activityFrequency(filteredStatuses.value, activityMap.value, 0, null))
const activityChartData = computed(() => ({
  labels: activityData.value.labels,
  datasets: [{ data: activityData.value.data, backgroundColor: '#0d9488aa', borderRadius: 4 }],
}))

// Dream charts

const dreamFreqData      = computed(() => dreamFrequency(filteredDreams.value, 0, null))
const dreamFreqChartData = computed(() => ({
  labels: dreamFreqData.value.labels,
  datasets: [{ data: dreamFreqData.value.data, backgroundColor: '#6366f1aa', borderRadius: 4 }],
}))

const dreamMoodDistRaw  = computed(() => moodDistribution(filteredDreams.value, moodMap.value, 0, null))
const dreamMoodDistData = computed(() => ({
  labels: dreamMoodDistRaw.value.labels,
  datasets: [{ data: dreamMoodDistRaw.value.data, backgroundColor: dreamMoodDistRaw.value.colors, borderWidth: 0 }],
}))

const avgDreamsPerWeek = computed(() => {
  const filtered = filteredDreams.value
  if (!filtered.length) return '0'
  let spanDays = yearMode.value ? 365 : rangeDays.value
  if (!spanDays && !yearMode.value) {
    const endMs = rangeEnd.value ? new Date(rangeEnd.value + 'T23:59:59').getTime() : Date.now()
    const first = new Date(Math.min(...filtered.map(d => new Date(d.timestamp).getTime())))
    spanDays = Math.max(7, Math.ceil((endMs - first.getTime()) / 86400000))
  }
  return (filtered.length / spanDays * 7).toFixed(1)
})

const avgDreamWords = computed(() => {
  const filtered = filteredDreams.value
  if (!filtered.length) return 0
  const total = filtered.reduce((s, d) => s + (d.content ?? '').split(/\s+/).filter(Boolean).length, 0)
  return Math.round(total / filtered.length)
})

// Weekday breakdown

const weekdayRaw = computed(() => weekdayStats(filteredStatuses.value, moodMap.value, 0, null))
const weekdayCountData = computed(() => ({
  labels: weekdayRaw.value.labels,
  datasets: [{ data: weekdayRaw.value.counts, backgroundColor: '#7c3aed66', borderRadius: 4 }],
}))
const weekdayMoodData = computed(() => ({
  labels: weekdayRaw.value.labels,
  datasets: [{ data: weekdayRaw.value.avgMoods, backgroundColor: '#f59e0b99', borderRadius: 4 }],
}))

// Habits

const habitData = computed(() => {
  if (yearMode.value) return habitCompletionRates(filteredHabitLogs.value, rawHabits.value, 0, null, filteredStatuses.value)
  return habitCompletionRates(rawHabitLogs.value, rawHabits.value, rangeDays.value, rangeEnd.value, allStatuses.value)
})

// Properties

const propertyCharts = computed(() =>
  allProperties.value
    .filter(p => p.type === 'scale')
    .map(p => ({
      id: p.id,
      name: p.name ?? '?',
      points: propertyOverTime(filteredStatuses.value, String(p.id), 0, null),
    }))
    .filter(pc => pc.points.length > 0)
    .map(pc => ({
      ...pc,
      chartData: {
        datasets: [{
          data: pc.points,
          borderColor: '#7c3aed',
          backgroundColor: 'rgba(124,58,237,0.08)',
          tension: 0.3,
          fill: true,
          pointRadius: pc.points.length > 60 ? 0 : 3,
          pointHoverRadius: 4,
        }],
      },
    }))
)

// Year-mode charts

const ACTIVITY_PALETTE = [
  '#7c3aed99', '#0d948899', '#f59e0b99', '#ef444499',
  '#6366f199', '#10b98199', '#f97316aa', '#8b5cf699',
]

const moodByMonthRaw  = computed(() => moodByMonth(filteredStatuses.value, moodMap.value))
const moodByMonthData = computed(() => {
  const vals = moodByMonthRaw.value
  const valid = vals.filter(v => v != null)
  const min = valid.length ? Math.min(...valid) : 0
  const max = valid.length ? Math.max(...valid) : 1
  const range = max - min
  const colors = vals.map(v => {
    if (v == null) return '#e7e5e4'
    const n = range > 0 ? (v - min) / range : 0.5
    if (n < 0.2) return '#fca5a5'
    if (n < 0.4) return '#fde68a'
    if (n < 0.6) return '#d6d3d1'
    if (n < 0.8) return '#a7f3d0'
    return '#6ee7b7'
  })
  return {
    labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    datasets: [{ data: vals, backgroundColor: colors, borderRadius: 4 }],
  }
})

const activitiesByMonthRaw  = computed(() => activitiesByMonth(filteredStatuses.value, activityMap.value))
const activitiesByMonthData = computed(() => ({
  labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
  datasets: activitiesByMonthRaw.value.map((act, i) => ({
    label: act.name,
    data: act.counts,
    backgroundColor: ACTIVITY_PALETTE[i % ACTIVITY_PALETTE.length],
    borderRadius: 2,
  })),
}))

// Chart options

const lineOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: {
      type: 'time',
      time: {
        tooltipFormat: 'MMM d, yyyy',
        displayFormats: { day: 'MMM d', week: 'MMM d', month: 'MMM yyyy' },
      },
      grid: { display: false },
      ticks: { maxTicksLimit: 6, font: { size: 10 }, color: '#a8a29e' },
    },
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 1 } },
  },
}
const doughnutOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 11 } } } },
}
const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 0 } },
  },
}
const hBarOptions = {
  indexAxis: 'y',
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: '#f5f5f4' }, ticks: { precision: 0 } },
    y: { grid: { display: false }, ticks: { font: { size: 11 } } },
  },
}
const dreamBarOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 0 } },
  },
}
const moodMonthOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 1 } },
  },
}
const stackedBarOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 6, font: { size: 10 } } } },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 10 } } },
    y: { stacked: true, grid: { color: '#f5f5f4' }, ticks: { precision: 0 } },
  },
}

// Data loading

async function load() {
  if (!ks.dataKey) return
  loading.value = true
  try {
    const [rawSt, rawMo, rawAc, rawDr, habitLogsRaw, rawHab, rawProps] = await Promise.all([
      dbGetAll('statuses'),
      dbGetAll('moods'),
      dbGetAll('activities'),
      dbGetAll('dreams'),
      dbGetAll('habit_logs'),
      dbGetAll('habits'),
      dbGetAll('properties'),
    ])
    const [statuses, moods, activities, dreams, habits, props] = await Promise.all([
      ks.decryptAll(rawSt),
      ks.decryptAll(rawMo),
      ks.decryptAll(rawAc),
      ks.decryptAll(rawDr),
      ks.decryptAll(rawHab),
      ks.decryptAll(rawProps),
    ])

    allStatuses.value = statuses
    allDreams.value   = dreams
    moodMap.value     = Object.fromEntries(moods.map(m => [m.id, m]))
    activityMap.value = Object.fromEntries(activities.map(a => [a.id, a]))
    calData.value     = calendarData(statuses, moodMap.value)
    rawHabitLogs.value = habitLogsRaw
    rawHabits.value    = habits.map(h => ({
      ...h,
      name: activityMap.value[h.activity_id]?.name ?? h.name ?? '?',
    }))
    allProperties.value = props
  } finally {
    loading.value = false
  }
}

watch(() => ks.dataKey, k => { if (k) load() })
watch(() => syncStore.revision, () => { if (ks.dataKey) load() })
onMounted(() => { if (ks.dataKey) load() })
</script>
