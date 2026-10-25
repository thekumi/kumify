<template>
    <div class="pb-nav">
        <TopBar title="Planner Settings" :back="true" />
        <div class="px-4 py-4 space-y-5">
            <section>
                <div class="flex items-center justify-between mb-2">
                    <h2 class="text-sm font-semibold text-stone-500 uppercase tracking-wide">Calendars</h2>
                    <button @click="showNewCalendar = true"
                            class="flex items-center gap-1 text-xs font-medium text-violet-600 hover:text-violet-700">
                        <i class="ph ph-plus"></i> New
                    </button>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
                    <div v-for="cal in plannerStore.calendars"
                         :key="cal.id"
                         class="flex items-center gap-3 px-4 py-3.5">
                        <span class="w-3 h-3 rounded-full shrink-0"
                              :style="{ background: cal.color }"></span>
                        <span class="flex-1 text-sm text-stone-800 truncate">
                            {{ cal.name || cal.virtual_key || '(unnamed)' }}
                            <span v-if="cal.virtual_key"
                                  class="ml-1.5 text-xs text-stone-400 font-normal">auto</span>
                        </span>
                        <button @click="toggleCalendarVisible(cal)"
                                class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                                :class="cal.is_visible ? 'bg-violet-600' : 'bg-stone-200'">
                            <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                                  :class="cal.is_visible ? 'translate-x-5' : 'translate-x-0'"></span>
                        </button>
                        <button v-if="!cal.virtual_key"
                                @click="editCalendar(cal)"
                                class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-stone-100 text-stone-400 transition-colors">
                            <i class="ph ph-pencil-simple text-sm"></i>
                        </button>
                    </div>
                    <div v-if="!plannerStore.calendars.length"
                         class="px-4 py-4 text-sm text-stone-400 text-center">No calendars yet</div>
                </div>
            </section>
            <section>
                <div class="flex items-center justify-between mb-2">
                    <h2 class="text-sm font-semibold text-stone-500 uppercase tracking-wide">Task Lists</h2>
                    <button @click="showNewTaskList = true"
                            class="flex items-center gap-1 text-xs font-medium text-violet-600 hover:text-violet-700">
                        <i class="ph ph-plus"></i> New
                    </button>
                </div>
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
                    <div v-for="list in plannerStore.taskLists"
                         :key="list.id"
                         class="flex items-center gap-3 px-4 py-3.5">
                        <span class="w-3 h-3 rounded-full shrink-0"
                              :style="{ background: list.color }"></span>
                        <span class="flex-1 text-sm text-stone-800 truncate">
                            {{ list.name || list.virtual_key || '(unnamed)' }}
                            <span v-if="list.virtual_key"
                                  class="ml-1.5 text-xs text-stone-400 font-normal">auto</span>
                        </span>
                        <button @click="toggleTaskListVisible(list)"
                                class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                                :class="list.is_visible ? 'bg-violet-600' : 'bg-stone-200'">
                            <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                                  :class="list.is_visible ? 'translate-x-5' : 'translate-x-0'"></span>
                        </button>
                        <button v-if="!list.virtual_key"
                                @click="editTaskList(list)"
                                class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-stone-100 text-stone-400 transition-colors">
                            <i class="ph ph-pencil-simple text-sm"></i>
                        </button>
                    </div>
                    <div v-if="!plannerStore.taskLists.length"
                         class="px-4 py-4 text-sm text-stone-400 text-center">No task lists yet</div>
                </div>
            </section>
        </div>
        <!-- New / Edit Calendar sheet -->
        <div v-if="showNewCalendar || editingCalendar"
             class="fixed inset-0 z-[60] flex items-end justify-center bg-black/40"
             @click.self="closeCalendarSheet">
            <div class="bg-white w-full max-w-lg rounded-t-2xl px-4 pt-5 pb-sheet space-y-3">
                <h3 class="font-semibold text-stone-800">{{ editingCalendar ? 'Edit Calendar' : 'New Calendar' }}</h3>
                <input v-model="calendarForm.name"
                       type="text"
                       placeholder="Calendar name"
                       class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                <div class="flex items-center gap-3">
                    <label class="text-sm text-stone-600 font-medium">Color</label>
                    <input v-model="calendarForm.color"
                           type="color"
                           class="h-8 w-16 rounded-lg cursor-pointer border border-stone-200" />
                </div>
                <template v-if="isAndroid">
                    <div class="flex items-center justify-between py-1">
                        <span class="text-sm text-stone-700 font-medium">Sync to system calendar</span>
                        <button @click="calendarForm.sync_to_system = !calendarForm.sync_to_system"
                                class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                                :class="calendarForm.sync_to_system ? 'bg-violet-600' : 'bg-stone-200'">
                            <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                                  :class="calendarForm.sync_to_system ? 'translate-x-5' : 'translate-x-0'"></span>
                        </button>
                    </div>
                    <p v-if="calendarForm.sync_to_system"
                       class="text-xs text-amber-700 bg-amber-50 rounded-xl px-3 py-2.5">
                        <i class="ph ph-warning mr-1"></i>Event titles will be visible to other apps installed on this device.
                    </p>
                </template>
                <div class="flex gap-2 pt-1">
                    <button @click="saveCalendar"
                            :disabled="!calendarForm.name.trim() || savingSheet"
                            class="flex-1 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors text-sm">
                        {{ savingSheet ? 'Saving…' : 'Save' }}
                    </button>
                    <button v-if="editingCalendar"
                            @click="removeCalendar"
                            class="px-5 py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                        Delete
                    </button>
                </div>
            </div>
        </div>
        <!-- New / Edit Task List sheet -->
        <div v-if="showNewTaskList || editingTaskList"
             class="fixed inset-0 z-[60] flex items-end justify-center bg-black/40"
             @click.self="closeTaskListSheet">
            <div class="bg-white w-full max-w-lg rounded-t-2xl px-4 pt-5 pb-sheet space-y-3">
                <h3 class="font-semibold text-stone-800">{{ editingTaskList ? 'Edit Task List' : 'New Task List' }}</h3>
                <input v-model="taskListForm.name"
                       type="text"
                       placeholder="List name"
                       class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                <div class="flex items-center gap-3">
                    <label class="text-sm text-stone-600 font-medium">Color</label>
                    <input v-model="taskListForm.color"
                           type="color"
                           class="h-8 w-16 rounded-lg cursor-pointer border border-stone-200" />
                </div>
                <div class="flex gap-2 pt-1">
                    <button @click="saveTaskList"
                            :disabled="!taskListForm.name.trim() || savingSheet"
                            class="flex-1 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors text-sm">
                        {{ savingSheet ? 'Saving…' : 'Save' }}
                    </button>
                    <button v-if="editingTaskList"
                            @click="removeTaskList"
                            class="px-5 py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                        Delete
                    </button>
                </div>
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
import { usePlannerStore } from '@/stores/planner'
import { removeSystemCalendar } from '@/planner/calendarSync'

const ks = useKeystoreStore()
const plannerStore = usePlannerStore()

const isAndroid = typeof window !== 'undefined' && !!window.Android

const showNewCalendar = ref(false)
const editingCalendar = ref(null)
const calendarForm = ref({ name: '', color: '#4A90D9', sync_to_system: false })

const showNewTaskList = ref(false)
const editingTaskList = ref(null)
const taskListForm = ref({ name: '', color: '#4A90D9' })

const savingSheet = ref(false)

onMounted(async () => {
  if (!plannerStore.loaded && ks.dataKey) await plannerStore.load(ks)
})

function editCalendar(cal) {
  editingCalendar.value = cal
  calendarForm.value = { name: cal.name ?? '', color: cal.color ?? '#4A90D9', sync_to_system: cal.sync_to_system ?? false }
}

function closeCalendarSheet() {
  showNewCalendar.value = false
  editingCalendar.value = null
  calendarForm.value = { name: '', color: '#4A90D9', sync_to_system: false }
}

async function saveCalendar() {
  if (!calendarForm.value.name.trim()) return
  savingSheet.value = true
  try {
    const wasSync = editingCalendar.value?.sync_to_system ?? false
    const willSync = calendarForm.value.sync_to_system
    if (editingCalendar.value) {
      await plannerStore.updateCalendar(ks, editingCalendar.value.id, calendarForm.value)
      if (wasSync && !willSync) removeSystemCalendar(editingCalendar.value.id)
    } else {
      await plannerStore.createCalendar(ks, calendarForm.value)
    }
    closeCalendarSheet()
  } finally {
    savingSheet.value = false
  }
}

async function removeCalendar() {
  if (!editingCalendar.value || !confirm('Delete this calendar and all its events?')) return
  if (editingCalendar.value.sync_to_system) removeSystemCalendar(editingCalendar.value.id)
  await plannerStore.deleteCalendar(editingCalendar.value.id)
  closeCalendarSheet()
}

async function toggleCalendarVisible(cal) {
  await plannerStore.updateCalendar(ks, cal.id, { is_visible: !cal.is_visible })
}

function editTaskList(list) {
  editingTaskList.value = list
  taskListForm.value = { name: list.name ?? '', color: list.color ?? '#4A90D9' }
}

function closeTaskListSheet() {
  showNewTaskList.value = false
  editingTaskList.value = null
  taskListForm.value = { name: '', color: '#4A90D9' }
}

async function saveTaskList() {
  if (!taskListForm.value.name.trim()) return
  savingSheet.value = true
  try {
    if (editingTaskList.value) {
      await plannerStore.updateTaskList(ks, editingTaskList.value.id, taskListForm.value)
    } else {
      await plannerStore.createTaskList(ks, taskListForm.value)
    }
    closeTaskListSheet()
  } finally {
    savingSheet.value = false
  }
}

async function removeTaskList() {
  if (!editingTaskList.value || !confirm('Delete this list and all its tasks?')) return
  await plannerStore.deleteTaskList(editingTaskList.value.id)
  closeTaskListSheet()
}

async function toggleTaskListVisible(list) {
  await plannerStore.updateTaskList(ks, list.id, { is_visible: !list.is_visible })
}
</script>
