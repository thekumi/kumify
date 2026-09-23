<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Dream' : 'Record Dream'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Title <span class="font-normal">(optional)</span></label>
          <input v-model="form.title" type="text" placeholder="Name this dream…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-2">Type</label>
          <div class="flex gap-2">
            <button v-for="(label, val) in types" :key="val" type="button"
              @click="form.type = Number(val)"
              class="flex-1 py-2 rounded-xl border text-sm font-medium transition-all"
              :class="form.type === Number(val) ? 'border-blue-400 bg-blue-50 text-blue-700' : 'border-stone-200 text-stone-600 hover:border-stone-300'">
              {{ label }}
            </button>
          </div>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-2">Dream content</label>
          <textarea v-model="form.content" rows="6" placeholder="What happened in your dream?"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-blue-400 text-stone-800 bg-stone-50 text-sm resize-none leading-relaxed"></textarea>
        </div>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.lucid" type="checkbox" class="w-4 h-4 rounded accent-blue-600" />
            <span class="text-sm text-stone-700 font-medium">Lucid dream</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.wet" type="checkbox" class="w-4 h-4 rounded accent-pink-500" />
            <span class="text-sm text-stone-700 font-medium">Wet dream</span>
          </label>
        </div>
      </div>

      <!-- Mood picker -->
      <div v-if="moods.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">How did you feel?</p>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="m in moods"
            :key="m.id"
            type="button"
            @click="form.mood = form.mood === m.id ? null : m.id"
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
      </div>

      <!-- Themes -->
      <div v-if="themes.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">Themes</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="t in themes"
            :key="t.id"
            type="button"
            @click="toggleTheme(t.id)"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm font-medium transition-all"
            :class="selectedThemes.has(t.id)
              ? 'border-blue-300 bg-blue-50 text-blue-700'
              : 'border-stone-200 text-stone-600 hover:border-stone-300'"
          >
            <i :class="t.icon || 'ph ph-tag'" :style="t.color ? `color:${t.color}` : ''" class="text-base"></i>
            {{ t.name }}
          </button>
        </div>
      </div>

      <!-- Attachments -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">Attachments</p>
        <div v-if="existingAttachments.length" class="mb-3">
          <MediaGallery :attachments="existingAttachments" :dataKey="ks.dataKey" :canDelete="true" :showPrivate="true" @delete="removeExistingAttachment" />
        </div>
        <div v-if="pendingFiles.length" class="space-y-2 mb-3">
          <div v-for="(pf, i) in pendingFiles" :key="i" class="flex items-center gap-2 bg-stone-50 rounded-xl px-3 py-2">
            <img v-if="pf.previewUrl" :src="pf.previewUrl" class="w-10 h-10 rounded-lg object-cover shrink-0" />
            <i v-else class="ph ph-file text-stone-400 text-xl shrink-0"></i>
            <span class="text-sm text-stone-700 truncate flex-1">{{ pf.file.name }}</span>
            <button type="button" @click="pf.private = !pf.private"
              class="shrink-0 flex items-center gap-1 text-xs px-2 py-1 rounded-lg transition-colors"
              :class="pf.private ? 'bg-amber-50 text-amber-600' : 'text-stone-400 hover:text-stone-600'">
              <i :class="pf.private ? 'ph ph-lock-simple' : 'ph ph-lock-simple-open'" class="text-sm"></i>
              {{ pf.private ? 'Private' : 'Visible' }}
            </button>
            <button type="button" @click="removePending(i)" class="text-stone-300 hover:text-red-400 transition-colors shrink-0">
              <i class="ph ph-x text-sm"></i>
            </button>
          </div>
        </div>
        <label class="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 cursor-pointer">
          <i class="ph ph-paperclip text-base"></i>
          Add files
          <input type="file" multiple class="hidden" @change="addFiles" />
        </label>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Record dream') }}
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
import MediaGallery from '@/components/MediaGallery.vue'
import { getDream, createDream, updateDream, getThemes, uploadDreamAttachment, deleteDreamAttachment } from '@/api/dreams'
import { getMoods } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const offline = useOfflineStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const types = { 0: 'Night', 1: 'Daydream', 2: 'Nap' }
const form = ref({ title: '', content: '', type: 0, lucid: false, wet: false, mood: null })
const moods = ref([])
const rawMoods = ref([])
const themes = ref([])
const selectedThemes = ref(new Set())
const existingAttachments = ref([])
const pendingFiles = ref([])
const saving = ref(false)
const error = ref('')
let rawDream = null

function addFiles(e) {
  for (const file of e.target.files) {
    const previewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : null
    pendingFiles.value.push({ file, previewUrl, private: false })
  }
  e.target.value = ''
}

function removePending(i) {
  const pf = pendingFiles.value[i]
  if (pf.previewUrl) URL.revokeObjectURL(pf.previewUrl)
  pendingFiles.value.splice(i, 1)
}

async function removeExistingAttachment(attachmentId) {
  if (!confirm('Remove this attachment?')) return
  try {
    await deleteDreamAttachment(id, attachmentId)
    existingAttachments.value = existingAttachments.value.filter(a => a.id !== attachmentId)
  } catch {
    error.value = 'Could not remove attachment.'
  }
}

async function uploadPending(dreamId) {
  for (const pf of pendingFiles.value) {
    try {
      await uploadDreamAttachment(dreamId, pf.file, ks.dataKey, pf.private)
    } catch (e) {
      console.warn('[dream form] attachment upload failed:', pf.file.name, e)
    }
  }
}

function toggleTheme(id) {
  selectedThemes.value.has(id) ? selectedThemes.value.delete(id) : selectedThemes.value.add(id)
}

async function applyDecryption() {
  moods.value = await ks.decryptAll(rawMoods.value)
}

watch(() => ks.dataKey, async (key) => {
  if (key) {
    await applyDecryption()
    if (rawDream) await fillForm(rawDream)
  }
})

async function fillForm(d) {
  const dec = await ks.decrypt(d)
  form.value = {
    title: dec.title ?? '',
    content: dec.content ?? '',
    type: dec.type ?? 0,
    lucid: dec.lucid ?? false,
    wet: dec.wet ?? false,
    mood: dec.mood ?? null,
  }
  selectedThemes.value = new Set((dec.themes ?? []).map(t => t.id))
}

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) {
      const result = await saveEncrypted(updateDream, id, { ...form.value, theme_ids: [...selectedThemes.value] }, ['title', 'content'], rawDream, ks)
      await uploadPending(result.id)
      router.push(`/journal/dreams/${result.id}`)
    } else {
      const toEncrypt = {}
      if (form.value.title) toEncrypt.title = form.value.title
      if (form.value.content) toEncrypt.content = form.value.content
      const createPayload = {
        type: form.value.type,
        lucid: form.value.lucid,
        wet: form.value.wet,
        mood: form.value.mood,
        theme_ids: [...selectedThemes.value],
        ...(Object.keys(toEncrypt).length ? { encrypted_payload: await ks.encryptPayload(toEncrypt) } : {}),
      }
      if (!navigator.onLine) {
        await offline.enqueue({ endpoint: '/dreams/', payload: createPayload })
        router.push('/journal/dreams')
      } else {
        try {
          const result = await createDream(createPayload)
          await uploadPending(result.id)
          router.push(`/journal/dreams/${result.id}`)
        } catch (e) {
          if (!(e instanceof TypeError)) throw e
          await offline.enqueue({ endpoint: '/dreams/', payload: createPayload })
          router.push('/journal/dreams')
        }
      }
    }
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

onMounted(async () => {
  const [m, t] = await Promise.all([getMoods().catch(() => []), getThemes().catch(() => [])])
  rawMoods.value = m
  themes.value = t
  await applyDecryption()

  if (id) {
    rawDream = await getDream(id)
    existingAttachments.value = rawDream.attachments ?? []
    await fillForm(rawDream)
  }
})
</script>
