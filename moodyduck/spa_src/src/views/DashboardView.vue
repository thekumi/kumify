<template>
  <div class="pb-nav">
    <TopBar title="MoodyDuck" />

    <div class="px-4 space-y-3 py-4">
      <!-- Stats row -->
      <div class="grid grid-cols-2 gap-3">
        <StatCard
          label="Total entries"
          :value="stats ? String(stats.total) : '—'"
          icon="ph ph-book-open"
          color="bg-clay-50 text-clay-700"
        />
        <StatCard
          label="Day streak"
          :value="stats ? `${stats.streak} days` : '—'"
          icon="ph ph-flame"
          color="bg-amber-50 text-amber-700"
        />
        <StatCard
          v-if="stats?.closest_mood"
          :label="`Avg mood (7d)`"
          :value="stats.closest_mood.name || '—'"
          :icon="stats.closest_mood.icon || 'ph ph-smiley'"
          :icon-color="stats.closest_mood.color"
          color="bg-sage-50 text-sage-700"
        />
        <StatCard
          v-if="stats?.top_activity"
          :label="`Top activity (7d)`"
          :value="stats.top_activity.name || '—'"
          :sub="`${stats.top_activity.count}×`"
          :icon="stats.top_activity.icon || 'ph ph-star'"
          :icon-color="stats.top_activity.color"
          color="bg-violet-50 text-violet-700"
        />
      </div>

      <!-- Quick actions -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-3">Quick add</p>
        <div class="flex gap-3">
          <RouterLink to="/mood/new" class="flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl bg-clay-50 hover:bg-clay-100 transition-colors">
            <i class="ph ph-smiley text-2xl text-clay-600"></i>
            <span class="text-xs font-medium text-clay-700">Mood</span>
          </RouterLink>
          <RouterLink to="/journal/dreams/new" class="flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors">
            <i class="ph ph-moon-stars text-2xl text-blue-600"></i>
            <span class="text-xs font-medium text-blue-700">Dream</span>
          </RouterLink>
          <RouterLink to="/journal/cbt/new" class="flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors">
            <i class="ph ph-brain text-2xl text-purple-600"></i>
            <span class="text-xs font-medium text-purple-700">Thought</span>
          </RouterLink>
          <RouterLink to="/health/logs/new" class="flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl bg-green-50 hover:bg-green-100 transition-colors">
            <i class="ph ph-heartbeat text-2xl text-green-600"></i>
            <span class="text-xs font-medium text-green-700">Health</span>
          </RouterLink>
        </div>
      </div>

      <!-- Recent moods -->
      <div v-if="recent.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm">
        <div class="flex items-center justify-between px-4 pt-4 pb-2">
          <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Recent</p>
          <RouterLink to="/mood" class="text-xs text-clay-600 font-medium">See all</RouterLink>
        </div>
        <ul class="divide-y divide-stone-50">
          <li v-for="s in recent" :key="s.id">
            <RouterLink :to="`/mood/${s.id}`" class="flex items-center gap-3 px-4 py-3 hover:bg-stone-50 transition-colors">
              <div class="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center shrink-0">
                <i
                  :class="s.mood?.icon || 'ph ph-smiley'"
                  :style="s.mood?.color ? `color:${s.mood.color}` : ''"
                  class="text-xl"
                ></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-stone-800 truncate">{{ s.mood?.name || 'Encrypted entry' }}</p>
                <p class="text-xs text-stone-400">{{ fmtDate(s.timestamp) }}</p>
              </div>
              <i class="ph ph-caret-right text-stone-300"></i>
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getDashboard, getStatuses, getMoods, getActivities } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const rawStats = ref(null)
const stats = ref(null)
const recent = ref([])
const rawMoods = ref([])
const rawActivities = ref([])
const rawStatuses = ref([])

function fmtDate(ts) {
  return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
}

async function applyDecryption() {
  const [decryptedMoods, decryptedActivities] = await Promise.all([
    ks.decryptAll(rawMoods.value),
    ks.decryptAll(rawActivities.value),
  ])
  const moodMap = Object.fromEntries(decryptedMoods.map(m => [m.id, m]))
  const activityMap = Object.fromEntries(decryptedActivities.map(a => [a.id, a]))

  recent.value = rawStatuses.value.slice(0, 5).map(st => ({
    ...st,
    mood: moodMap[st.mood] ?? null,
  }))

  if (rawStats.value) {
    const s = { ...rawStats.value }
    if (s.closest_mood?.id) {
      const m = moodMap[s.closest_mood.id]
      if (m) s.closest_mood = { ...s.closest_mood, name: m.name, icon: m.icon, color: m.color }
    }
    if (s.top_activity?.id) {
      const a = activityMap[s.top_activity.id]
      if (a) s.top_activity = { ...s.top_activity, name: a.name, icon: a.icon, color: a.color }
    }
    stats.value = s
  }
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

onMounted(async () => {
  const [s, page, moods, activities] = await Promise.all([
    getDashboard().catch(() => null),
    getStatuses(1).catch(() => ({ results: [] })),
    getMoods().catch(() => []),
    getActivities().catch(() => []),
  ])
  rawStats.value = s
  stats.value = s
  rawMoods.value = moods
  rawActivities.value = activities
  rawStatuses.value = page.results ?? []
  await applyDecryption()
})
</script>

<script>
// Inline stat card to keep this file self-contained
import { defineComponent, h } from 'vue'
const StatCard = defineComponent({
  props: ['label', 'value', 'icon', 'color', 'iconColor', 'sub'],
  setup(props) {
    return () => h('div', { class: `rounded-2xl border border-stone-100 shadow-sm p-4 bg-white` }, [
      h('div', { class: 'flex items-start justify-between' }, [
        h('div', [
          h('p', { class: 'text-xs font-medium text-stone-400' }, props.label),
          h('p', { class: 'text-xl font-bold text-stone-800 mt-0.5 leading-tight' }, props.value),
          props.sub ? h('p', { class: 'text-xs text-stone-400 mt-0.5' }, props.sub) : null,
        ]),
        h('i', {
          class: `${props.icon} text-2xl`,
          style: props.iconColor ? `color:${props.iconColor}` : '',
        }),
      ]),
    ])
  },
})
export default { components: { StatCard } }
</script>
