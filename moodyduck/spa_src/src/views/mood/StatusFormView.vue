<template>
  <div class="pb-nav">
    <TopBar :title="isEdit ? 'Edit Entry' : 'New Entry'" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="save" class="px-4 py-4 space-y-4">
      <!-- Mood picker -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">How are you feeling?</p>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="m in moods"
            :key="m.id"
            type="button"
            @click="form.mood = m.id"
            class="flex flex-col items-center gap-1 p-2 rounded-xl transition-all"
            :class="form.mood === m.id ? 'ring-2 ring-offset-1 bg-stone-50' : 'hover:bg-stone-50'"
            :style="form.mood === m.id && m.color ? `--tw-ring-color:${m.color}` : ''"
          >
            <i :class="m.icon || 'ph ph-smiley'"
               :style="m.color ? `color:${m.color}` : ''"
               class="text-3xl"></i>
            <span class="text-xs text-stone-600 truncate w-full text-center">{{ m.name || '—' }}</span>
          </button>
        </div>
        <p v-if="!moods.length" class="text-sm text-stone-400 text-center py-2">
          <RouterLink to="/mood/settings/moods" class="text-clay-600 underline">Add some moods</RouterLink> first.
        </p>
      </div>

      <!-- Title -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <label class="text-sm font-semibold text-stone-500 block mb-2">Title <span class="font-normal">(optional)</span></label>
        <input v-model="form.title" type="text" placeholder="Give this moment a name…"
          class="w-full text-stone-800 placeholder-stone-300 border-0 outline-none text-sm" />
      </div>

      <!-- Text -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <label class="text-sm font-semibold text-stone-500 block mb-2">Notes <span class="font-normal">(optional)</span></label>
        <textarea v-model="form.text" rows="5" placeholder="What's on your mind?"
          class="w-full text-stone-800 placeholder-stone-300 border-0 outline-none text-sm resize-none leading-relaxed"></textarea>
      </div>

      <!-- Activities -->
      <div v-if="activities.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">Activities</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="a in activities"
            :key="a.id"
            type="button"
            @click="toggleActivity(a.id)"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm font-medium transition-all"
            :class="selectedActivities.has(a.id)
              ? 'border-clay-300 bg-clay-50 text-clay-700'
              : 'border-stone-200 text-stone-600 hover:border-stone-300'"
          >
            <i :class="a.icon || 'ph ph-check'" :style="a.color ? `color:${a.color}` : ''" class="text-base"></i>
            {{ a.name || '—' }}
          </button>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (isEdit ? 'Save changes' : 'Add entry') }}
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getMoods, getActivities, getStatus, createStatus, updateStatus } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const offline = useOfflineStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const isEdit = !!id

const moods = ref([])
const activities = ref([])
const rawMoods = ref([])
const rawActivities = ref([])
const form = ref({ mood: null, title: '', text: '' })
const selectedActivities = ref(new Set())
const loading = ref(true)
const saving = ref(false)
const error = ref('')
let rawStatus = null

function toggleActivity(id) {
  selectedActivities.value.has(id)
    ? selectedActivities.value.delete(id)
    : selectedActivities.value.add(id)
}

async function applyDecryption() {
  moods.value = await ks.decryptAll(rawMoods.value)
  activities.value = await ks.decryptAll(rawActivities.value)
  if (rawStatus && isEdit) {
    const s = await ks.decrypt(rawStatus)
    form.value.title = s.title ?? ''
    form.value.text = s.text ?? ''
  }
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      mood: form.value.mood,
      title: form.value.title || null,
      text: form.value.text || null,
      activity_ids: [...selectedActivities.value],
    }
    if (isEdit) {
      const result = await saveEncrypted(updateStatus, id, payload, ['title', 'text'], rawStatus, ks)
      router.push(`/mood/${result.id}`)
    } else if (!navigator.onLine) {
      await offline.enqueue({ endpoint: '/statuses/', payload })
      router.push('/mood')
    } else {
      try {
        const result = await createStatus(payload)
        router.push(`/mood/${result.id}`)
      } catch (e) {
        if (!(e instanceof TypeError)) throw e
        await offline.enqueue({ endpoint: '/statuses/', payload })
        router.push('/mood')
      }
    }
  } catch {
    error.value = 'Could not save. Please try again.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [m, a] = await Promise.all([getMoods().catch(() => []), getActivities().catch(() => [])])
  rawMoods.value = m
  rawActivities.value = a
  await applyDecryption()

  if (isEdit) {
    rawStatus = await getStatus(id)
    form.value.mood = rawStatus.mood
    selectedActivities.value = new Set(rawStatus.activities?.map(a => a.id) ?? [])
    const s = await ks.decrypt(rawStatus)
    form.value.title = s.title ?? ''
    form.value.text = s.text ?? ''
  }
  loading.value = false
})
</script>
