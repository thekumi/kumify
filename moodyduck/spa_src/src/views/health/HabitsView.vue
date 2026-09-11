<template>
  <div class="pb-nav">
    <TopBar title="Habits" :back="true">
      <template #actions>
        <button @click="showNew = true" class="w-8 h-8 flex items-center justify-center rounded-full bg-amber-100 hover:bg-amber-200 transition-colors">
          <i class="ph ph-plus text-amber-700"></i>
        </button>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-amber-200 border-t-amber-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!habits.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-check-circle text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No habits defined yet</p>
      <button @click="showNew = true" class="mt-4 px-5 py-2.5 bg-amber-600 text-white rounded-xl text-sm font-medium hover:bg-amber-700 transition-colors">
        Add habit
      </button>
    </div>

    <ul v-else class="mx-4 mt-4 space-y-2">
      <li v-for="h in habits" :key="h.id" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
             :style="h.color ? `background:${h.color}22` : 'background:#f5f5f4'">
          <i :class="h.icon || 'ph ph-check-circle'"
             :style="h.color ? `color:${h.color}` : 'color:#a8a29e'"
             class="text-xl"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="font-medium text-stone-800 truncate">{{ h.name }}</p>
          <p v-if="h.description" class="text-xs text-stone-400 truncate">{{ h.description }}</p>
        </div>
        <button @click="logHabit(h)"
          class="px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 text-sm font-medium hover:bg-amber-100 transition-colors">
          ✓ Log
        </button>
      </li>
    </ul>

    <!-- New habit inline form -->
    <div v-if="showNew" class="fixed inset-0 bg-black/30 z-50 flex items-end" @click.self="showNew = false">
      <div class="bg-white w-full rounded-t-3xl p-6 space-y-4">
        <h2 class="text-lg font-semibold text-stone-800">New Habit</h2>
        <input v-model="newHabit.name" type="text" placeholder="Habit name" autofocus
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-400 text-stone-800 bg-stone-50 text-sm" />
        <div class="flex gap-3">
          <button @click="showNew = false" class="flex-1 py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
          <button @click="createHabit" :disabled="!newHabit.name" class="flex-1 py-3 rounded-xl bg-amber-600 text-white text-sm font-medium hover:bg-amber-700 transition-colors disabled:opacity-50">Create</button>
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
import { getHabits, createHabit as apiCreate, createHabitLog } from '@/api/habits'

const habits = ref([])
const loading = ref(true)
const showNew = ref(false)
const newHabit = ref({ name: '' })

async function logHabit(h) {
  await createHabitLog({ habit: h.id })
  alert(`Logged: ${h.name}`)
}

async function createHabit() {
  await apiCreate({ name: newHabit.value.name })
  newHabit.value.name = ''
  showNew.value = false
  habits.value = await getHabits()
}

onMounted(async () => { habits.value = await getHabits(); loading.value = false })
</script>
