<template>
    <div class="pb-nav">
        <TopBar title="Error Log" :back="true" />
        <div class="px-4 py-4 space-y-3">
            <!-- Filter -->
            <div class="flex rounded-xl border border-stone-200 overflow-hidden text-sm font-medium">
                <button v-for="opt in filterOptions"
                        :key="opt.value"
                        type="button"
                        @click="filter = opt.value; load()"
                        class="flex-1 py-2 transition-colors"
                        :class="filter === opt.value ? 'bg-clay-600 text-white' : 'bg-white text-stone-500 hover:bg-stone-50'">
                    {{ opt.label }}
                </button>
            </div>
            <div v-if="loading" class="flex justify-center py-12">
                <div class="w-7 h-7 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
            </div>
            <template v-else>
                <div v-if="!logs.length"
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm px-4 py-8 text-center">
                    <i class="ph ph-check-circle text-3xl text-stone-300 block mb-2"></i>
                    <p class="text-sm text-stone-400">No errors logged.</p>
                </div>
                <div v-for="log in logs"
                     :key="log.id"
                     class="bg-white rounded-2xl border shadow-sm overflow-hidden"
                     :class="log.resolved ? 'border-stone-100' : 'border-red-100'">
                    <!-- Header -->
                    <button type="button"
                            @click="toggle(log)"
                            class="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-stone-50 transition-colors">
                        <i class="ph mt-0.5 shrink-0 text-lg"
                           :class="log.resolved ? 'ph-check-circle text-stone-300' : 'ph-warning text-red-400'"></i>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-semibold text-stone-800 truncate">{{ log.exception_type }}</p>
                            <p class="text-xs text-stone-400 truncate mt-0.5">{{ log.exception_value }}</p>
                            <p class="text-xs text-stone-300 mt-1">
                                {{ log.method }} {{ log.path }}
                                <span v-if="log.username">· {{ log.username }}</span>
                                · {{ formatDate(log.timestamp) }}
                            </p>
                        </div>
                        <i class="ph text-stone-300 mt-0.5 shrink-0"
                           :class="expanded === log.id ? 'ph-caret-up' : 'ph-caret-down'"></i>
                    </button>
                    <!-- Expanded detail -->
                    <div v-if="expanded === log.id"
                         class="border-t border-stone-100 px-4 py-3 space-y-3">
                        <pre class="text-xs text-stone-600 bg-stone-50 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap break-words font-mono">{{ log.traceback }}</pre>
                        <button type="button"
                                @click="toggleResolved(log)"
                                class="w-full py-2.5 rounded-xl text-sm font-semibold transition-colors"
                                :class="log.resolved
                                    ? 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                                    : 'bg-green-600 text-white hover:bg-green-700'">
                            {{ log.resolved ? 'Mark unresolved' : 'Mark resolved' }}
                        </button>
                    </div>
                </div>
            </template>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getErrorLogs, patchErrorLog } from '@/api/errorlog'

const logs = ref([])
const loading = ref(true)
const expanded = ref(null)
const filter = ref('unresolved')

const filterOptions = [
  { value: 'unresolved', label: 'Unresolved' },
  { value: 'all',        label: 'All' },
  { value: 'resolved',   label: 'Resolved' },
]

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

function toggle(log) {
  expanded.value = expanded.value === log.id ? null : log.id
}

async function load() {
  loading.value = true
  try {
    const resolved = filter.value === 'resolved' ? true
                   : filter.value === 'unresolved' ? false
                   : null
    logs.value = await getErrorLogs(resolved)
  } finally {
    loading.value = false
  }
}

async function toggleResolved(log) {
  const next = !log.resolved
  try {
    await patchErrorLog(log.id, { resolved: next })
    log.resolved = next
    if (filter.value !== 'all') logs.value = logs.value.filter(l => l.id !== log.id)
  } catch {
    // leave state unchanged
  }
}

onMounted(load)
</script>
