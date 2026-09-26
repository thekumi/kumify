<template>
  <div>
    <!-- Trigger row -->
    <div class="flex items-center gap-3 cursor-pointer" @click="open = true">
      <div class="w-12 h-12 rounded-xl border border-stone-200 bg-stone-50 flex items-center justify-center shrink-0">
        <i :class="modelValue || fallback" :style="color ? `color:${color}` : ''" class="text-2xl"></i>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm text-stone-700 truncate font-mono">{{ modelValue || fallback }}</p>
        <p class="text-xs text-stone-400">Tap to change</p>
      </div>
      <i class="ph ph-caret-right text-stone-300 text-lg shrink-0"></i>
    </div>

    <!-- Bottom sheet -->
    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 bg-black/30 z-50 flex items-end" @click.self="open = false">
        <div class="bg-white w-full rounded-t-3xl flex flex-col" style="max-height:80vh">
          <div class="flex items-center gap-3 px-5 pt-5 pb-3 shrink-0">
            <i class="ph ph-magnifying-glass text-stone-400 text-lg"></i>
            <input ref="searchEl" v-model="query" type="search" placeholder="Search icons…"
              class="flex-1 text-sm text-stone-800 border-0 outline-none bg-transparent placeholder-stone-300" />
            <button type="button" @click="open = false" class="text-stone-400 hover:text-stone-600">
              <i class="ph ph-x text-lg"></i>
            </button>
          </div>
          <div class="overflow-y-auto px-4 pb-6">
            <template v-for="group in filtered" :key="group.label">
              <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mt-4 mb-2">{{ group.label }}</p>
              <div class="grid grid-cols-7 gap-1.5">
                <button v-for="icon in group.icons" :key="icon" type="button"
                  @click="pick(icon)"
                  class="w-full aspect-square rounded-xl flex items-center justify-center transition-all"
                  :class="modelValue === `ph ${icon}`
                    ? 'bg-clay-100 ring-2 ring-clay-400'
                    : 'bg-stone-50 hover:bg-stone-100'">
                  <i :class="`ph ${icon}`" :style="modelValue === `ph ${icon}` && color ? `color:${color}` : ''" class="text-xl"></i>
                </button>
              </div>
            </template>
            <p v-if="!filtered.length" class="text-sm text-stone-400 text-center py-8">No icons found.</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  fallback: { type: String, default: 'ph ph-circle' },
  color: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const searchEl = ref(null)

watch(open, (v) => {
  if (v) { query.value = ''; nextTick(() => searchEl.value?.focus()) }
})

function pick(icon) {
  emit('update:modelValue', `ph ${icon}`)
  open.value = false
}

const ICONS = [
  { label: 'Emotions', icons: [
    'ph-smiley', 'ph-smiley-wink', 'ph-smiley-melting', 'ph-smiley-nervous', 'ph-smiley-sad',
    'ph-smiley-meh', 'ph-smiley-angry', 'ph-smiley-blank', 'ph-smiley-x-eyes', 'ph-smiley-sticker',
    'ph-heart', 'ph-heart-break', 'ph-heart-half', 'ph-star', 'ph-star-half',
    'ph-thumbs-up', 'ph-thumbs-down', 'ph-hands-clapping', 'ph-hand-peace', 'ph-hand-heart',
    'ph-zzz', 'ph-lightning', 'ph-fire', 'ph-snowflake', 'ph-rainbow',
  ]},
  { label: 'People & Social', icons: [
    'ph-user', 'ph-user-circle', 'ph-users', 'ph-users-three', 'ph-user-plus',
    'ph-handshake', 'ph-chat', 'ph-chat-dots', 'ph-chat-circle', 'ph-chats',
    'ph-phone', 'ph-video-camera', 'ph-envelope', 'ph-house', 'ph-buildings',
    'ph-baby', 'ph-dog', 'ph-cat', 'ph-bird', 'ph-fish',
  ]},
  { label: 'Activity & Sports', icons: [
    'ph-person-simple-run', 'ph-person-simple-walk', 'ph-person-simple-swim', 'ph-person-simple-bike',
    'ph-barbell', 'ph-bicycle', 'ph-football', 'ph-soccer-ball', 'ph-basketball',
    'ph-tennis-ball', 'ph-golf', 'ph-ping-pong', 'ph-bowling-ball',
    'ph-person-simple-ski', 'ph-snowboard', 'ph-boat', 'ph-horse', 'ph-yoga',
    'ph-hand-fist', 'ph-trophy',
  ]},
  { label: 'Health & Body', icons: [
    'ph-heartbeat', 'ph-brain', 'ph-lungs', 'ph-tooth', 'ph-eye',
    'ph-drop', 'ph-drop-half', 'ph-apple', 'ph-leaf', 'ph-plant',
    'ph-pill', 'ph-bandaids', 'ph-first-aid-kit', 'ph-hospital',
    'ph-moon', 'ph-sun', 'ph-bed', 'ph-thermometer', 'ph-scales', 'ph-shield-check',
  ]},
  { label: 'Food & Drink', icons: [
    'ph-fork-knife', 'ph-bowl-food', 'ph-coffee', 'ph-glass-water', 'ph-wine',
    'ph-beer-bottle', 'ph-cake', 'ph-carrot', 'ph-cookie', 'ph-ice-cream',
    'ph-pizza', 'ph-hamburger', 'ph-shrimp', 'ph-egg', 'ph-cheese',
  ]},
  { label: 'Work & Learning', icons: [
    'ph-briefcase', 'ph-laptop', 'ph-desktop', 'ph-monitor', 'ph-keyboard',
    'ph-book', 'ph-books', 'ph-notebook', 'ph-pencil', 'ph-pencil-simple',
    'ph-lightbulb', 'ph-magnifying-glass', 'ph-chart-bar', 'ph-chart-line', 'ph-chart-pie',
    'ph-calculator', 'ph-calendar', 'ph-clock', 'ph-timer', 'ph-alarm',
    'ph-wrench', 'ph-scissors', 'ph-ruler', 'ph-palette', 'ph-music-note',
    'ph-headphones', 'ph-guitar', 'ph-camera', 'ph-film-clapperboard', 'ph-paint-brush',
  ]},
  { label: 'Nature & Travel', icons: [
    'ph-tree', 'ph-tree-palm', 'ph-flower', 'ph-flower-lotus', 'ph-mountain',
    'ph-sun-horizon', 'ph-cloud', 'ph-cloud-rain', 'ph-wind', 'ph-waves',
    'ph-planet', 'ph-moon-stars', 'ph-star-four', 'ph-shooting-star',
    'ph-airplane', 'ph-car', 'ph-train', 'ph-map-pin', 'ph-map-trifold',
    'ph-anchor', 'ph-tent', 'ph-compass', 'ph-rocket', 'ph-umbrella',
  ]},
  { label: 'Misc', icons: [
    'ph-check-circle', 'ph-check', 'ph-x-circle', 'ph-warning', 'ph-info',
    'ph-flag', 'ph-bookmark', 'ph-tag', 'ph-gift', 'ph-confetti',
    'ph-coin', 'ph-wallet', 'ph-piggy-bank', 'ph-shopping-bag', 'ph-key',
    'ph-lock', 'ph-globe', 'ph-wifi', 'ph-power', 'ph-recycle',
  ]},
]

const filtered = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return ICONS
  return ICONS.map(g => ({
    label: g.label,
    icons: g.icons.filter(ic => ic.replace('ph-', '').includes(q)),
  })).filter(g => g.icons.length)
})
</script>
