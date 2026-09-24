<template>
  <div class="pb-nav">
    <TopBar title="Habits" :back="true">
      <template #actions>
        <button @click="openNew" class="w-8 h-8 flex items-center justify-center rounded-full bg-amber-100 hover:bg-amber-200 transition-colors">
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
      <button @click="openNew" class="mt-4 px-5 py-2.5 bg-amber-600 text-white rounded-xl text-sm font-medium hover:bg-amber-700 transition-colors">
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
          <p class="font-medium text-stone-800 truncate">{{ h.name || '—' }}</p>
          <p v-if="h.description" class="text-xs text-stone-400 truncate">{{ h.description }}</p>
          <p v-if="h.goal" class="text-xs text-stone-300">{{ h.goal.target_count }}× {{ h.goal.period }}</p>
        </div>
        <button @click="logHabit(h)" title="Log"
          class="w-8 h-8 flex items-center justify-center rounded-full bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100 transition-colors text-sm font-bold shrink-0">
          ✓
        </button>
        <button @click="openEdit(h)" title="Edit"
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
          <i class="ph ph-pencil-simple text-stone-400"></i>
        </button>
      </li>
    </ul>

    <!-- New / Edit habit sheet -->
    <div v-if="sheet" class="fixed inset-0 bg-black/30 z-50 flex items-end" @click.self="sheet = null">
      <div class="bg-white w-full rounded-t-3xl p-6 space-y-4">
        <h2 class="text-lg font-semibold text-stone-800">{{ sheet.id ? 'Edit Habit' : 'New Habit' }}</h2>
        <input v-model="sheet.name" type="text" placeholder="Habit name" autofocus
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-400 text-stone-800 bg-stone-50 text-sm" />
        <textarea v-model="sheet.description" rows="2" placeholder="Description (optional)"
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" v-model="sheet.goalEnabled" class="rounded accent-amber-600" />
            <span class="text-sm text-stone-600">Set a goal</span>
          </label>
          <div v-if="sheet.goalEnabled" class="flex items-center gap-2">
            <div class="flex gap-0.5 bg-stone-100 rounded-xl p-0.5">
              <button v-for="p in ['daily','weekly','monthly']" :key="p"
                @click="sheet.goalPeriod = p"
                class="text-xs px-2.5 py-1.5 rounded-lg capitalize font-medium transition-colors"
                :class="sheet.goalPeriod === p ? 'bg-white shadow-sm text-stone-800' : 'text-stone-400'">
                {{ p }}
              </button>
            </div>
            <input type="number" v-model.number="sheet.goalCount" min="1" max="99"
              class="w-14 px-2 py-2 rounded-xl border border-stone-200 text-center text-sm text-stone-800 bg-stone-50 focus:outline-none focus:ring-2 focus:ring-amber-400" />
            <span class="text-sm text-stone-400">× / {{ sheet.goalPeriod === 'daily' ? 'day' : sheet.goalPeriod === 'weekly' ? 'week' : 'month' }}</span>
          </div>
        </div>
        <p v-if="sheetError" class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ sheetError }}</p>
        <div class="flex gap-3">
          <button v-if="sheet.id" @click="removeHabit(sheet)" type="button"
            class="py-3 px-4 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
            Delete
          </button>
          <button @click="sheet = null" class="flex-1 py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
          <button @click="saveHabit" :disabled="!sheet.name || sheetSaving"
            class="flex-1 py-3 rounded-xl bg-amber-600 text-white text-sm font-medium hover:bg-amber-700 transition-colors disabled:opacity-50">
            {{ sheetSaving ? 'Saving…' : (sheet.id ? 'Save' : 'Create') }}
          </button>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getHabits, createHabit, updateHabit, deleteHabit, createHabitLog } from '@/api/habits'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const habits = ref([])
const raw = ref([])
const loading = ref(true)
const sheet = ref(null)
const sheetSaving = ref(false)
const sheetError = ref('')

const ENCRYPTED_FIELDS = ['name', 'description', 'goal']

async function applyDecryption() { habits.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

function openNew() {
  sheet.value = { name: '', description: '', goalEnabled: false, goalPeriod: 'weekly', goalCount: 1 }
  sheetError.value = ''
}

function openEdit(h) {
  const rawHabit = raw.value.find(r => r.id === h.id)
  sheet.value = {
    id: h.id, _raw: rawHabit,
    name: h.name ?? '', description: h.description ?? '',
    goalEnabled: !!h.goal,
    goalPeriod: h.goal?.period ?? 'weekly',
    goalCount: h.goal?.target_count ?? 1,
  }
  sheetError.value = ''
}

async function saveHabit() {
  if (!sheet.value.name) return
  sheetSaving.value = true; sheetError.value = ''
  const goal = sheet.value.goalEnabled ? { target_count: sheet.value.goalCount, period: sheet.value.goalPeriod } : null
  try {
    if (sheet.value.id) {
      await saveEncrypted(updateHabit, sheet.value.id, { name: sheet.value.name, description: sheet.value.description, goal }, ENCRYPTED_FIELDS, sheet.value._raw, ks)
    } else {
      const toEncrypt = { name: sheet.value.name }
      if (sheet.value.description) toEncrypt.description = sheet.value.description
      if (goal) toEncrypt.goal = goal
      const encrypted_payload = await ks.encryptPayload(toEncrypt)
      await createHabit({ encrypted_payload })
    }
    sheet.value = null
    raw.value = await getHabits()
    await applyDecryption()
  } catch { sheetError.value = 'Could not save.' }
  finally { sheetSaving.value = false }
}

async function removeHabit(h) {
  if (!confirm('Delete this habit?')) return
  await deleteHabit(h.id)
  sheet.value = null
  raw.value = await getHabits()
  await applyDecryption()
}

async function logHabit(h) {
  await createHabitLog({ habit: h.id })
}

onMounted(async () => {
  raw.value = await getHabits()
  await applyDecryption()
  loading.value = false
})
</script>
