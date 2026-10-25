<template>
    <div class="pb-nav">
        <TopBar title="Health Statistics" :back="true" />
        <div v-if="loading"
             class="flex flex-col items-center justify-center py-20 gap-3">
            <div class="w-8 h-8 border-4 border-stone-200 border-t-green-500 rounded-full animate-spin"></div>
            <p class="text-sm text-stone-400">Loading your data…</p>
        </div>
        <div v-else class="px-4 py-4 space-y-4">
            <!-- Range selector -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-1 flex">
                <button v-for="d in [7, 30, 90, 365, 0]"
                        :key="d"
                        type="button"
                        @click="rangeDays = d"
                        class="flex-1 text-xs py-2 rounded-xl font-medium transition-colors"
                        :class="rangeDays === d ? 'bg-green-100 text-green-700' : 'text-stone-400 hover:text-stone-600'">
                    {{ d === 0 ? 'All' : d + 'd' }}
                </button>
            </div>
            <!-- Time navigation -->
            <div v-if="rangeDays"
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
            <div class="grid grid-cols-3 gap-2">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ filteredLogs.length }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Logs</p>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ activeDays }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Active days</p>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-3 text-center">
                    <p class="text-2xl font-bold text-stone-800">{{ trackedParams }}</p>
                    <p class="text-xs text-stone-400 mt-0.5">Parameters</p>
                </div>
            </div>
            <!-- Per-parameter trends -->
            <template v-if="paramCharts.length">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Parameters</p>
                <div v-for="pc in paramCharts"
                     :key="pc.id"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <div class="flex items-center gap-2 mb-2">
                        <i :class="[pc.icon, 'text-green-600 text-base']"></i>
                        <p class="text-sm font-semibold text-stone-700">
                            {{ pc.name }}
                            <span v-if="pc.unit" class="text-xs font-normal text-stone-400 ml-1">{{ pc.unit }}</span>
                        </p>
                    </div>
                    <div class="grid grid-cols-3 gap-2 mb-3">
                        <div class="text-center bg-stone-50 rounded-xl py-2">
                            <p class="text-base font-bold text-stone-800">{{ pc.min }}</p>
                            <p class="text-xs text-stone-400">Min</p>
                        </div>
                        <div class="text-center bg-stone-50 rounded-xl py-2">
                            <p class="text-base font-bold text-stone-800">{{ pc.avg }}</p>
                            <p class="text-xs text-stone-400">Avg</p>
                        </div>
                        <div class="text-center bg-stone-50 rounded-xl py-2">
                            <p class="text-base font-bold text-stone-800">{{ pc.max }}</p>
                            <p class="text-xs text-stone-400">Max</p>
                        </div>
                    </div>
                    <div v-if="pc.points.length > 1" class="h-36">
                        <Line :data="pc.chartData" :options="lineOptions" />
                    </div>
                    <p v-else
                       class="text-xs text-stone-400 text-center py-2">Only one data point — add more logs to see a trend</p>
                </div>
            </template>
            <!-- Log frequency -->
            <template v-if="freqData.labels.length > 1">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider pt-1">Frequency</p>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                    <p class="text-sm font-semibold text-stone-700 mb-3">Logs over time</p>
                    <div class="h-40">
                        <Bar :data="freqChartData" :options="barOptions" />
                    </div>
                </div>
            </template>
            <p v-if="!filteredLogs.length"
               class="text-center text-stone-400 text-sm py-8">No health logs yet — start tracking!</p>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, TimeScale,
  PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { decryptPayload } from '@/keystore/fields'
import { dbGetAll } from '@/lib/db'
import { filterByDays, healthParameterOverTime } from '@/history/stats.js'

ChartJS.register(CategoryScale, LinearScale, TimeScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

const ks = useKeystoreStore()
const loading = ref(true)
const rangeDays = ref(30)
const rangeEnd = ref(null)

watch(rangeDays, () => { rangeEnd.value = null })

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

const allLogs = ref([])
const allParameters = ref([])

const filteredLogs = computed(() => filterByDays(allLogs.value, rangeDays.value, l => l.recorded_at, rangeEnd.value))

const activeDays = computed(() => new Set(filteredLogs.value.map(l => l.recorded_at.slice(0, 10))).size)

const trackedParams = computed(() => {
  const ids = new Set()
  for (const log of filteredLogs.value) {
    for (const r of (log.records ?? [])) {
      if (r.parameter?.id != null) ids.add(r.parameter.id)
    }
  }
  return ids.size
})

const paramCharts = computed(() =>
  allParameters.value
    .map(param => {
      const points = healthParameterOverTime(allLogs.value, param.id, rangeDays.value, rangeEnd.value)
      if (!points.length) return null
      const vals = points.map(p => p.y)
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length
      const fmt = (v) => Number.isInteger(v) ? v : +v.toFixed(2)
      return {
        id: param.id,
        name: param.name ?? '?',
        unit: param.unit ?? '',
        icon: param.icon || 'ph ph-chart-line',
        points,
        min: fmt(Math.min(...vals)),
        max: fmt(Math.max(...vals)),
        avg: fmt(avg),
        chartData: {
          datasets: [{
            data: points,
            borderColor: '#16a34a',
            backgroundColor: 'rgba(22,163,74,0.08)',
            tension: 0.3,
            fill: true,
            pointRadius: points.length > 60 ? 0 : 3,
            pointHoverRadius: 4,
          }],
        },
      }
    })
    .filter(Boolean)
)

const freqData = computed(() => {
  const filtered = filteredLogs.value
  if (!filtered.length) return { labels: [], data: [] }
  const useMonths = !rangeDays.value || rangeDays.value > 100
  const byPeriod = {}
  for (const log of filtered) {
    const date = new Date(log.recorded_at)
    let key
    if (useMonths) {
      key = date.toISOString().slice(0, 7)
    } else {
      const dow = date.getDay() === 0 ? 6 : date.getDay() - 1
      const monday = new Date(date)
      monday.setDate(date.getDate() - dow)
      key = monday.toISOString().slice(0, 10)
    }
    byPeriod[key] = (byPeriod[key] || 0) + 1
  }
  const entries = Object.entries(byPeriod).sort(([a], [b]) => a.localeCompare(b))
  return {
    labels: entries.map(([k]) =>
      useMonths
        ? new Date(k + '-01T12:00:00').toLocaleString('default', { month: 'short', year: 'numeric' })
        : new Date(k + 'T12:00:00').toLocaleDateString('default', { month: 'short', day: 'numeric' })
    ),
    data: entries.map(([, c]) => c),
  }
})

const freqChartData = computed(() => ({
  labels: freqData.value.labels,
  datasets: [{ data: freqData.value.data, backgroundColor: '#16a34a99', borderRadius: 4 }],
}))

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
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 2 } },
  },
}

const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    y: { grid: { color: '#f5f5f4' }, ticks: { precision: 0 } },
  },
}

async function decryptLogs(rawLogs) {
  const decrypted = await ks.decryptAll(rawLogs)
  return Promise.all(decrypted.map(async (log) => {
    if (!ks.dataKey || !log.records?.length) return log
    const records = await Promise.all(log.records.map(async (r) => {
      const recDec = r.encrypted_payload
        ? await decryptPayload(ks.dataKey, r.encrypted_payload).catch(() => ({}))
        : {}
      const paramDec = r.parameter?.encrypted_payload
        ? await decryptPayload(ks.dataKey, r.parameter.encrypted_payload).catch(() => ({}))
        : {}
      return { ...r, ...recDec, parameter: { ...r.parameter, ...paramDec } }
    }))
    return { ...log, records }
  }))
}

async function load() {
  if (!ks.dataKey) return
  loading.value = true
  try {
    const [rawLogs, rawParams] = await Promise.all([dbGetAll('health_logs'), dbGetAll('health_parameters')])
    const [decryptedParams, decryptedLogs] = await Promise.all([
      ks.decryptAll(rawParams),
      decryptLogs(rawLogs),
    ])
    allParameters.value = decryptedParams
    allLogs.value = decryptedLogs
  } finally {
    loading.value = false
  }
}

watch(() => ks.dataKey, (k) => { if (k) load() })
onMounted(() => { if (ks.dataKey) load() })
</script>
