<template>
    <div>
        <div class="flex gap-2 px-4 py-3 overflow-x-auto scrollbar-none">
            <button v-for="list in visibleLists"
                    :key="list.id"
                    @click="selectedList = list"
                    class="flex-none px-3 py-1.5 rounded-full text-sm font-medium transition-colors whitespace-nowrap"
                    :class="selectedList?.id === list.id
                        ? 'text-white'
                        : 'bg-stone-100 text-stone-600 hover:bg-stone-200'"
                    :style="selectedList?.id === list.id ? { background: list.color ?? '#6366F1' } : {}">
                {{ list.name || list.virtual_key || '(list)' }}
            </button>
        </div>
        <div v-if="!selectedList"
             class="flex flex-col items-center py-16 text-center px-6">
            <i class="ph ph-check-square text-5xl text-stone-300 mb-3"></i>
            <p class="text-stone-400 text-sm">Select a task list above</p>
        </div>
        <div v-else>
            <div v-if="loadingTasks" class="flex justify-center py-12">
                <div class="w-7 h-7 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
            </div>
            <div v-else-if="!tasks.length"
                 class="flex flex-col items-center py-12 text-center px-6">
                <i class="ph ph-check text-5xl text-stone-300 mb-3"></i>
                <p class="text-stone-400 text-sm">No tasks</p>
                <button v-if="!selectedList.virtual_key"
                        @click="showAddTask = true"
                        class="mt-4 px-5 py-2 bg-violet-600 text-white rounded-xl text-sm font-medium hover:bg-violet-700 transition-colors">
                    Add task
                </button>
            </div>
            <ul v-else
                class="mx-4 bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
                <li v-for="task in tasks"
                    :key="task.id"
                    class="flex items-center gap-3 px-4 py-3.5">
                    <button v-if="!task.virtual"
                            @click="toggleDone(task)"
                            class="w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 transition-colors"
                            :class="task.done ? 'bg-violet-600 border-violet-600' : 'border-stone-300 hover:border-violet-400'">
                        <i v-if="task.done" class="ph ph-check text-white text-xs"></i>
                    </button>
                    <span v-else
                          class="w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0"
                          :class="task.done ? 'bg-violet-600 border-violet-600' : 'border-stone-200'">
                        <i v-if="task.done" class="ph ph-check text-white text-xs"></i>
                    </span>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm text-stone-800 truncate"
                           :class="task.done ? 'line-through text-stone-400' : ''">{{ task.title || '(task)' }}</p>
                        <p v-if="task.due_date" class="text-xs text-stone-400 mt-0.5">{{ task.due_date }}</p>
                    </div>
                    <i v-if="!task.virtual && PRIORITY_INDICATOR[task.priority]"
                       :class="[PRIORITY_INDICATOR[task.priority].icon, 'text-sm shrink-0']"
                       :style="{ color: PRIORITY_INDICATOR[task.priority].color }"></i>
                    <span v-if="task.virtual" class="text-xs text-stone-300 italic shrink-0">auto</span>
                    <template v-else>
                        <button @click="openEdit(task)"
                                class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-stone-100 text-stone-400 transition-colors shrink-0">
                            <i class="ph ph-pencil-simple text-sm"></i>
                        </button>
                        <button @click="removeTask(task)"
                                class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-red-50 text-stone-300 hover:text-red-400 transition-colors shrink-0">
                            <i class="ph ph-trash text-sm"></i>
                        </button>
                    </template>
                </li>
            </ul>
            <div class="px-4 mt-3">
                <button v-if="!selectedList.virtual_key && !showAddTask"
                        @click="showAddTask = true"
                        class="w-full py-3 rounded-xl border border-dashed border-stone-300 text-stone-400 text-sm hover:border-violet-400 hover:text-violet-500 transition-colors flex items-center justify-center gap-1">
                    <i class="ph ph-plus"></i> Add task
                </button>
                <form v-if="showAddTask" @submit.prevent="addTask" class="space-y-2 mt-2">
                    <input v-model="newTaskTitle"
                           ref="newTaskInput"
                           type="text"
                           placeholder="Task name"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                    <div class="flex gap-1.5">
                        <button v-for="p in PRIORITIES"
                                :key="p.value"
                                type="button"
                                @click="newTaskPriority = p.value"
                                class="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                :class="newTaskPriority === p.value ? p.activeClass : 'bg-stone-100 text-stone-400'">
                            <i :class="p.icon" class="text-xs"></i>{{ p.label }}
                        </button>
                    </div>
                    <div class="flex gap-2">
                        <input v-model="newTaskReminder"
                               type="datetime-local"
                               class="flex-1 px-3 py-2 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-700 bg-stone-50 text-sm" />
                        <button type="submit"
                                :disabled="!newTaskTitle.trim()"
                                class="px-4 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-medium disabled:opacity-50 hover:bg-violet-700 transition-colors shrink-0">
                            Add
                        </button>
                    </div>
                </form>
            </div>
        </div>
        <!-- Edit task sheet -->
        <div v-if="editingTask"
             class="fixed inset-0 z-[60] flex items-end justify-center bg-black/40"
             @click.self="closeEdit">
            <div class="bg-white w-full max-w-lg rounded-t-2xl px-4 pt-5 pb-sheet space-y-3">
                <h3 class="font-semibold text-stone-800">Edit Task</h3>
                <input v-model="editTaskTitle"
                       type="text"
                       placeholder="Task name"
                       class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                <div>
                    <label class="text-xs text-stone-500 font-medium block mb-1">Priority</label>
                    <div class="flex gap-1.5">
                        <button v-for="p in PRIORITIES"
                                :key="p.value"
                                type="button"
                                @click="editTaskPriority = p.value"
                                class="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                :class="editTaskPriority === p.value ? p.activeClass : 'bg-stone-100 text-stone-400'">
                            <i :class="p.icon" class="text-xs"></i>{{ p.label }}
                        </button>
                    </div>
                </div>
                <div>
                    <label class="text-xs text-stone-500 font-medium block mb-1">Reminder</label>
                    <input v-model="editTaskReminder"
                           type="datetime-local"
                           class="w-full px-3 py-2 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-700 bg-stone-50 text-sm" />
                </div>
                <div class="flex gap-2 pt-1">
                    <button @click="saveEdit"
                            :disabled="!editTaskTitle.trim() || savingEdit"
                            class="flex-1 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors text-sm">
                        {{ savingEdit ? 'Saving…' : 'Save' }}
                    </button>
                    <button @click="closeEdit"
                            class="px-5 py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useKeystoreStore } from '@/stores/keystore'
import { getTasks, createTask, updateTask, deleteTask as apiDeleteTask } from '@/api/planner'
import { getTaskListProvider } from '@/planner/registry'
import { scheduleReminder, cancelReminder } from '@/planner/reminders'

const props = defineProps({
  taskLists: { type: Array, default: () => [] },
})

const ks = useKeystoreStore()

const PRIORITIES = [
  { value: 0, label: 'None',   icon: 'ph ph-minus',     activeClass: 'bg-stone-200 text-stone-600' },
  { value: 1, label: 'Low',    icon: 'ph ph-flag',       activeClass: 'bg-blue-100 text-blue-600'   },
  { value: 2, label: 'Medium', icon: 'ph ph-flag',       activeClass: 'bg-amber-100 text-amber-600' },
  { value: 3, label: 'High',   icon: 'ph ph-flag-fill',  activeClass: 'bg-red-100 text-red-600'     },
]
const PRIORITY_INDICATOR = {
  1: { icon: 'ph ph-flag',      color: '#93c5fd' },
  2: { icon: 'ph ph-flag',      color: '#fbbf24' },
  3: { icon: 'ph ph-flag-fill', color: '#ef4444' },
}

function sortedTasks(arr) {
  return [...arr].sort((a, b) => (b.priority || 0) - (a.priority || 0))
}

const visibleLists = computed(() => props.taskLists.filter(l => l.is_visible))
const selectedList = ref(null)
const tasks = ref([])
const loadingTasks = ref(false)
const showAddTask = ref(false)
const newTaskTitle = ref('')
const newTaskReminder = ref('')
const newTaskPriority = ref(0)
const newTaskInput = ref(null)

const editingTask = ref(null)
const editTaskTitle = ref('')
const editTaskReminder = ref('')
const editTaskPriority = ref(0)
const savingEdit = ref(false)

watch(visibleLists, (lists) => {
  if (!selectedList.value && lists.length) selectedList.value = lists[0]
  else if (selectedList.value && !lists.find(l => l.id === selectedList.value.id)) {
    selectedList.value = lists[0] ?? null
  }
}, { immediate: true })

watch(selectedList, () => {
  showAddTask.value = false
  newTaskTitle.value = ''
  if (selectedList.value) loadTasksForList()
})

watch(showAddTask, async (show) => {
  if (show) {
    await nextTick()
    newTaskInput.value?.focus()
  }
})

async function loadTasksForList() {
  if (!selectedList.value || !ks.dataKey) return
  loadingTasks.value = true
  tasks.value = []
  try {
    const list = selectedList.value
    if (list.virtual_key) {
      const fn = getTaskListProvider(list.virtual_key)
      tasks.value = fn ? await fn(ks).catch(() => []) : []
    } else {
      const raw = await getTasks({ task_list: list.id })
      tasks.value = sortedTasks(await ks.decryptAll(raw))
    }
  } finally {
    loadingTasks.value = false
  }
}

watch(() => ks.dataKey, (key) => { if (key && selectedList.value) loadTasksForList() })

async function toggleDone(task) {
  const done = !task.done
  const done_at = done ? new Date().toISOString() : null
  task.done = done
  task.done_at = done_at
  await updateTask(task.id, { done, done_at })
}

async function addTask() {
  if (!newTaskTitle.value.trim() || !selectedList.value) return
  const title = newTaskTitle.value.trim()
  const reminder_at = newTaskReminder.value ? new Date(newTaskReminder.value).toISOString() : null
  const payload = { title }
  if (newTaskPriority.value > 0) payload.priority = newTaskPriority.value
  const encrypted_payload = await ks.encryptPayload(payload)
  const body = { task_list: selectedList.value.id, encrypted_payload }
  if (reminder_at) body.reminder_at = reminder_at
  const raw = await createTask(body)
  const dec = await ks.decrypt(raw)
  tasks.value = sortedTasks([...tasks.value, dec])
  if (reminder_at) {
    scheduleReminder(raw, title)
    if (window.Android?.canScheduleExactAlarms?.() === false) {
      if (confirm('For accurate reminders, grant exact alarm permission. Open settings?')) {
        window.Android?.requestExactAlarmPermission?.()
      }
    }
  }
  newTaskTitle.value = ''
  newTaskReminder.value = ''
  newTaskPriority.value = 0
  showAddTask.value = false
}

function openEdit(task) {
  editingTask.value = task
  editTaskTitle.value = task.title || ''
  editTaskReminder.value = task.reminder_at
    ? new Date(task.reminder_at).toISOString().slice(0, 16)
    : ''
  editTaskPriority.value = task.priority || 0
}

function closeEdit() {
  editingTask.value = null
  editTaskTitle.value = ''
  editTaskReminder.value = ''
  editTaskPriority.value = 0
}

async function saveEdit() {
  if (!editingTask.value || !editTaskTitle.value.trim()) return
  savingEdit.value = true
  try {
    const title = editTaskTitle.value.trim()
    const payload = { title, priority: editTaskPriority.value || undefined }
    const encrypted_payload = await ks.encryptPayload(payload)
    const reminder_at = editTaskReminder.value
      ? new Date(editTaskReminder.value).toISOString()
      : null
    const body = { encrypted_payload, reminder_at }
    const raw = await updateTask(editingTask.value.id, body)
    const dec = await ks.decrypt(raw)
    tasks.value = sortedTasks(tasks.value.map(t => t.id === editingTask.value.id ? dec : t))
    if (reminder_at) scheduleReminder(raw, title)
    else cancelReminder(editingTask.value.id)
    closeEdit()
  } finally {
    savingEdit.value = false
  }
}

async function removeTask(task) {
  if (!confirm('Delete this task?')) return
  await apiDeleteTask(task.id)
  cancelReminder(task.id)
  tasks.value = tasks.value.filter(t => t.id !== task.id)
}

function triggerAddTask() {
  if (!selectedList.value?.virtual_key) showAddTask.value = true
}

defineExpose({ triggerAddTask })
</script>
