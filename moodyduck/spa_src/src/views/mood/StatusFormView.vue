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

      <!-- Custom properties -->
      <div v-if="properties.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">Custom</p>
        <div class="space-y-3">
          <div v-for="p in properties" :key="p.id">
            <p class="text-xs text-stone-500 mb-1.5">{{ p.name || '—' }}</p>
            <button v-if="p.type === 'boolean'" type="button"
              @click="toggleProperty(p.id)"
              class="px-4 py-1.5 rounded-full border text-sm font-medium transition-all"
              :class="form.properties[String(p.id)]
                ? 'border-clay-300 bg-clay-50 text-clay-700'
                : 'border-stone-200 text-stone-500 hover:border-stone-300'">
              {{ form.properties[String(p.id)] ? 'Yes' : 'No' }}
            </button>
            <div v-else-if="(p.max_val - p.min_val) <= 9" class="flex gap-1 flex-wrap">
              <button v-for="v in scaleRange(p)" :key="v" type="button"
                @click="setProperty(p.id, v)"
                class="w-8 h-8 rounded-lg border text-sm font-medium transition-all"
                :class="form.properties[String(p.id)] === v
                  ? 'border-clay-300 bg-clay-50 text-clay-700'
                  : 'border-stone-200 text-stone-500 hover:border-stone-300'">
                {{ v }}
              </button>
            </div>
            <div v-else class="flex items-center gap-2">
              <span class="text-xs text-stone-400 w-6 text-right">{{ p.min_val }}</span>
              <input type="range" :min="p.min_val" :max="p.max_val" :step="1"
                :value="form.properties[String(p.id)] ?? p.min_val"
                @input="setProperty(p.id, Number($event.target.value))"
                class="flex-1 accent-clay-600" />
              <span class="text-xs text-stone-600 w-6">{{ form.properties[String(p.id)] ?? p.min_val }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Attachments -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <p class="text-sm font-semibold text-stone-500 mb-3">Attachments</p>

        <!-- Existing attachments (edit mode) -->
        <div v-if="existingAttachments.length" class="mb-3">
          <MediaGallery
            :attachments="existingAttachments"
            :dataKey="ks.dataKey"
            :canDelete="true"
            :showPrivate="true"
            @delete="removeExistingAttachment"
          />
        </div>

        <!-- Pending new files -->
        <div v-if="pendingFiles.length" class="space-y-2 mb-3">
          <div v-for="(pf, i) in pendingFiles" :key="i"
               class="flex items-center gap-2 bg-stone-50 rounded-xl px-3 py-2">
            <img v-if="pf.previewUrl" :src="pf.previewUrl"
                 class="w-10 h-10 rounded-lg object-cover shrink-0" />
            <i v-else class="ph ph-file text-stone-400 text-xl shrink-0"></i>
            <span class="text-sm text-stone-700 truncate flex-1">{{ pf.file.name }}</span>
            <button type="button" @click="pf.private = !pf.private"
              class="shrink-0 flex items-center gap-1 text-xs px-2 py-1 rounded-lg transition-colors"
              :class="pf.private ? 'bg-amber-50 text-amber-600' : 'text-stone-400 hover:text-stone-600'">
              <i :class="pf.private ? 'ph ph-lock-simple' : 'ph ph-lock-simple-open'" class="text-sm"></i>
              {{ pf.private ? 'Private' : 'Visible' }}
            </button>
            <button type="button" @click="removePending(i)"
              class="text-stone-300 hover:text-red-400 transition-colors shrink-0">
              <i class="ph ph-x text-sm"></i>
            </button>
          </div>
        </div>

        <label class="inline-flex items-center gap-1.5 text-sm text-clay-600 hover:text-clay-700 cursor-pointer">
          <i class="ph ph-paperclip text-base"></i>
          Add files
          <input type="file" multiple class="hidden" @change="addFiles" />
        </label>
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
import MediaGallery from '@/components/MediaGallery.vue'
import { getMoods, getActivities, getStatus, createStatus, updateStatus, uploadAttachment, deleteAttachment } from '@/api/mood'
import { getProperties } from '@/api/properties'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'

const ks = useKeystoreStore()
const offline = useOfflineStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const isEdit = !!id

const moods = ref([])
const activities = ref([])
const properties = ref([])
const rawMoods = ref([])
const rawActivities = ref([])
const rawProperties = ref([])
const form = ref({ mood: null, title: '', text: '', properties: {} })
const selectedActivities = ref(new Set())
const existingAttachments = ref([])
const pendingFiles = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
let rawStatus = null

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
    await deleteAttachment(id, attachmentId)
    existingAttachments.value = existingAttachments.value.filter(a => a.id !== attachmentId)
  } catch {
    error.value = 'Could not remove attachment.'
  }
}

function scaleRange(p) {
  const result = []
  for (let v = p.min_val; v <= p.max_val; v++) result.push(v)
  return result
}

function toggleProperty(id) {
  const key = String(id)
  form.value.properties[key] = !form.value.properties[key]
}

function setProperty(id, v) {
  form.value.properties[String(id)] = v
}

function toggleActivity(id) {
  selectedActivities.value.has(id)
    ? selectedActivities.value.delete(id)
    : selectedActivities.value.add(id)
}

async function applyDecryption() {
  const dm = await ks.decryptAll(rawMoods.value)
  dm.sort((a, b) => (Number(b.value) || 0) - (Number(a.value) || 0))
  moods.value = dm
  activities.value = await ks.decryptAll(rawActivities.value)
  properties.value = await ks.decryptAll(rawProperties.value)
  if (rawStatus && isEdit) {
    const s = await ks.decrypt(rawStatus)
    form.value.title = s.title ?? ''
    form.value.text = s.text ?? ''
    form.value.mood = s.mood_id != null ? Number(s.mood_id) : (rawStatus.mood ?? null)
    selectedActivities.value = new Set(
      s.activity_ids != null
        ? JSON.parse(s.activity_ids)
        : (rawStatus.activities?.map(a => a.id) ?? [])
    )
    form.value.properties = (s.properties && typeof s.properties === 'object') ? s.properties : {}
  }
}

watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

async function uploadPending(statusId) {
  for (const pf of pendingFiles.value) {
    try {
      await uploadAttachment(statusId, pf.file, ks.dataKey, pf.private)
    } catch (e) {
      console.warn('[form] attachment upload failed:', pf.file.name, e)
    }
  }
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const toEncrypt = {}
    if (form.value.title) toEncrypt.title = form.value.title
    if (form.value.text) toEncrypt.text = form.value.text
    if (form.value.mood != null) toEncrypt.mood_id = String(form.value.mood)
    const actIds = [...selectedActivities.value]
    if (actIds.length) toEncrypt.activity_ids = JSON.stringify(actIds)
    const propEntries = Object.entries(form.value.properties).filter(([, v]) => v != null)
    if (propEntries.length) toEncrypt.properties = Object.fromEntries(propEntries)

    if (isEdit) {
      const encrypted_payload = await ks.encryptPayload(toEncrypt)
      const result = await updateStatus(id, { encrypted_payload, mood: null, activity_ids: [] })
      await uploadPending(result.id)
      router.push(`/mood/${result.id}`)
    } else {
      const createPayload = Object.keys(toEncrypt).length
        ? { encrypted_payload: await ks.encryptPayload(toEncrypt) }
        : {}
      if (!navigator.onLine) {
        await offline.enqueue({ endpoint: '/statuses/', payload: createPayload })
        router.push('/mood')
      } else {
        try {
          const result = await createStatus(createPayload)
          await uploadPending(result.id)
          router.push(`/mood/${result.id}`)
        } catch (e) {
          if (!(e instanceof TypeError)) throw e
          await offline.enqueue({ endpoint: '/statuses/', payload: createPayload })
          router.push('/mood')
        }
      }
    }
  } catch {
    error.value = 'Could not save. Please try again.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [m, a, p] = await Promise.all([getMoods().catch(() => []), getActivities().catch(() => []), getProperties().catch(() => [])])
  rawMoods.value = m
  rawActivities.value = a
  rawProperties.value = p
  await applyDecryption()

  if (isEdit) {
    rawStatus = await getStatus(id)
    existingAttachments.value = rawStatus.attachments ?? []
    await applyDecryption()
  }
  loading.value = false
})
</script>
