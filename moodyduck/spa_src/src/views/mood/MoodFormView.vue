<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Mood' : 'New Mood'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
          <input v-model="form.name" type="text" required placeholder="e.g. Happy"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Icon class <span class="font-normal text-xs">(Phosphor CSS class)</span></label>
          <div class="flex items-center gap-3">
            <input v-model="form.icon" type="text" placeholder="ph ph-smiley"
              class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
            <i :class="form.icon || 'ph ph-smiley'" :style="form.color ? `color:${form.color}` : ''" class="text-3xl shrink-0"></i>
          </div>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Color</label>
          <div class="flex items-center gap-3">
            <input v-model="form.color" type="color"
              class="w-10 h-10 rounded-xl border border-stone-200 cursor-pointer p-0.5 bg-stone-50" />
            <span class="text-sm text-stone-500 font-mono">{{ form.color }}</span>
          </div>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Value <span class="font-normal">(1–255, used for averages)</span></label>
          <input v-model.number="form.value" type="number" min="1" max="255" placeholder="128"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Create mood') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete mood
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
import { getMoods, createMood, updateMood, deleteMood } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', icon: 'ph ph-smiley', color: '#d4703f', value: null })
const saving = ref(false)
const error = ref('')
let rawMood = null

async function fillForm(mood) {
  const m = await ks.decrypt(mood)
  form.value = { name: m.name ?? '', icon: m.icon ?? 'ph ph-smiley', color: m.color ?? '#d4703f', value: m.value }
}

watch(() => ks.dataKey, async (key) => { if (key && rawMood) await fillForm(rawMood) })

async function save() {
  saving.value = true
  error.value = ''
  try {
    if (id) await saveEncrypted(updateMood, id, form.value, ['name', 'icon', 'color', 'value'], rawMood, ks)
    else await createMood(form.value)
    router.push('/mood/settings/moods')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this mood?')) return
  await deleteMood(id)
  router.push('/mood/settings/moods')
}

onMounted(async () => {
  if (id) {
    const moods = await getMoods()
    rawMood = moods.find(m => String(m.id) === String(id))
    if (rawMood) await fillForm(rawMood)
  }
})
</script>
