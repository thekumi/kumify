<template>
    <div class="pb-nav">
        <TopBar title="Import from Daylio" :back="true" />
        <div class="px-4 py-4 space-y-4">
            <!-- pick -->
            <template v-if="stage === 'pick'">
                <div v-if="mapLoading"
                     class="flex items-center justify-center gap-3 py-12">
                    <div class="w-5 h-5 border-2 border-stone-200 border-t-clay-600 rounded-full animate-spin shrink-0"></div>
                    <p class="text-sm text-stone-500">Analysing file…</p>
                </div>
                <div v-else
                     class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5 space-y-4">
                    <p class="text-sm text-stone-500">
                        Import from a Daylio
                        <code class="bg-stone-100 px-1 rounded text-xs">.daylio</code>
                        backup file. In Daylio: Settings → Backup &amp; Restore → Export.
                    </p>
                    <label class="flex flex-col items-center justify-center gap-3 border-2 border-dashed border-stone-200 rounded-xl p-8 cursor-pointer hover:border-clay-300 hover:bg-stone-50 transition-colors">
                        <i class="ph ph-upload-simple text-4xl text-stone-300"></i>
                        <span class="text-sm text-stone-500 font-medium">Choose .daylio file</span>
                        <input ref="fileInput"
                               type="file"
                               accept=".daylio"
                               class="hidden"
                               @change="onFileChange" />
                    </label>
                </div>
                <p v-if="parseError"
                   class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ parseError }}</p>
            </template>
            <!-- map -->
            <template v-if="stage === 'map'">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 grid grid-cols-2 gap-3 text-center">
                    <div>
                        <p class="text-2xl font-bold text-stone-800">{{ mappedMoods.filter(m => m.matchId != null).length }}</p>
                        <p class="text-xs text-stone-400">Moods matched</p>
                    </div>
                    <div>
                        <p class="text-2xl font-bold text-clay-600">{{ mappedMoods.filter(m => m.matchId == null).length }}</p>
                        <p class="text-xs text-stone-400">Moods new</p>
                    </div>
                    <div>
                        <p class="text-2xl font-bold text-stone-800">{{ mappedActivities.filter(a => a.matchId != null).length }}</p>
                        <p class="text-xs text-stone-400">Activities matched</p>
                    </div>
                    <div>
                        <p class="text-2xl font-bold text-clay-600">{{ mappedActivities.filter(a => a.matchId == null).length }}</p>
                        <p class="text-xs text-stone-400">Activities new</p>
                    </div>
                </div>
                <div>
                    <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider px-1 mb-2">Moods</p>
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden divide-y divide-stone-50">
                        <div v-for="m in mappedMoods"
                             :key="m.daylio.id"
                             class="flex items-center gap-3 px-4 py-3">
                            <div class="w-3 h-3 rounded-full shrink-0"
                                 :style="`background:${m.daylio.color}`"></div>
                            <p class="flex-1 text-sm font-medium text-stone-700">{{ m.daylio.name }}</p>
                            <i :class="m.matchId != null ? 'ph ph-check text-green-500' : 'ph ph-plus text-stone-300'"
                               class="text-sm shrink-0"></i>
                            <select v-model="m.matchId"
                                    class="text-sm border border-stone-200 rounded-lg px-2 py-1.5 bg-white text-stone-700 max-w-[160px]">
                                <option :value="null">Create new</option>
                                <option v-for="em in existingMoods" :key="em.id" :value="em.id">{{ em.name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div>
                    <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider px-1 mb-2">Activities</p>
                    <div class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden divide-y divide-stone-50">
                        <div v-for="a in mappedActivities"
                             :key="a.daylio.id"
                             class="flex items-center gap-3 px-4 py-3">
                            <p class="flex-1 text-sm font-medium text-stone-700">{{ a.daylio.name }}</p>
                            <i :class="a.matchId != null ? 'ph ph-check text-green-500' : 'ph ph-plus text-stone-300'"
                               class="text-sm shrink-0"></i>
                            <select v-model="a.matchId"
                                    class="text-sm border border-stone-200 rounded-lg px-2 py-1.5 bg-white text-stone-700 max-w-[160px]">
                                <option :value="null">Create new</option>
                                <option v-for="ea in existingActivities"
                                        :key="ea.id"
                                        :value="ea.id">{{ ea.name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button @click="confirmMapping"
                        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 text-white font-semibold rounded-xl transition-colors">
                    Continue
                </button>
                <button @click="resetPick"
                        class="w-full py-2.5 text-sm text-stone-500 hover:text-stone-700 transition-colors">
                    Choose a different file
                </button>
            </template>
            <!-- preview -->
            <template v-if="stage === 'preview'">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm overflow-hidden divide-y divide-stone-50">
                    <p class="px-4 pt-3 pb-1 text-xs font-semibold text-stone-400 uppercase tracking-wider">Ready to import</p>
                    <div v-for="s in STEPS"
                         :key="s.key"
                         class="flex items-center justify-between px-4 py-3">
                        <p class="text-sm text-stone-600">{{ s.label }}</p>
                        <p class="text-sm font-semibold text-stone-800">{{ totals[s.key] }}</p>
                    </div>
                </div>
                <label class="flex items-start gap-3 px-1 cursor-pointer">
                    <input type="checkbox"
                           v-model="updateExisting"
                           class="mt-0.5 accent-clay-600" />
                    <span class="text-xs text-stone-500">
                        Update existing entries
                        <span class="text-stone-400">(re-imports already-imported entries to repair corrupted text from the previous encoding bug)</span>
                    </span>
                </label>
                <p v-if="!updateExisting"
                   class="text-xs text-stone-400 px-1">Already-imported entries will be skipped automatically.</p>
                <button @click="startImport"
                        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 text-white font-semibold rounded-xl transition-colors">
                    Start import
                </button>
                <button @click="stage = 'map'"
                        class="w-full py-2.5 text-sm text-stone-500 hover:text-stone-700 transition-colors">
                    Back to mapping
                </button>
                <button @click="resetPick"
                        class="w-full py-2.5 text-sm text-stone-500 hover:text-stone-700 transition-colors">
                    Choose a different file
                </button>
            </template>
            <!-- importing -->
            <template v-if="stage === 'importing'">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5 space-y-4">
                    <div class="flex items-center gap-2">
                        <div class="w-4 h-4 border-2 border-stone-200 border-t-clay-600 rounded-full animate-spin shrink-0"></div>
                        <p class="text-sm font-semibold text-stone-700">Importing…</p>
                    </div>
                    <div class="space-y-3">
                        <div v-for="s in activeSteps" :key="s.key">
                            <div class="flex items-center justify-between mb-1.5">
                                <p class="text-sm text-stone-600">{{ s.label }}</p>
                                <p class="text-xs text-stone-400">{{ progress[s.key] }} / {{ totals[s.key] }}</p>
                            </div>
                            <div class="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                                <div class="h-full bg-clay-500 rounded-full transition-all duration-200"
                                     :style="{ width: pct(s.key) }"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
            <!-- done -->
            <template v-if="stage === 'done'">
                <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5 space-y-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                             :class="importError ? 'bg-amber-100' : 'bg-green-100'">
                            <i :class="importError ? 'ph ph-warning text-amber-600' : 'ph ph-check text-green-600'"
                               class="text-xl"></i>
                        </div>
                        <div>
                            <p class="text-sm font-semibold text-stone-800">
                                {{ importError ? 'Import finished with errors' : 'Import complete' }}
                            </p>
                            <p class="text-xs text-stone-400 mt-0.5">{{ results.created.entries }} entries created</p>
                        </div>
                    </div>
                    <div class="border-t border-stone-50 pt-3 space-y-2">
                        <div v-for="s in STEPS"
                             :key="s.key"
                             class="flex items-center justify-between text-sm">
                            <span class="text-stone-500">{{ s.label }}</span>
                            <span>
                                <span class="font-medium text-stone-700">{{ results.created[s.key] }} new</span>
                                <span class="text-stone-400">, {{ results.skipped[s.key] }} existing</span>
                            </span>
                        </div>
                    </div>
                    <p v-if="importError"
                       class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ importError }}</p>
                </div>
                <RouterLink to="/mood" class="block w-full py-3.5 bg-clay-600 hover:bg-clay-700 text-white font-semibold rounded-xl transition-colors text-center">
                View entries
                </RouterLink>
                <button @click="resetPick"
                        class="w-full py-2.5 text-sm text-stone-500 hover:text-stone-700 transition-colors">
                    Import another file
                </button>
            </template>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import {
  createMood,
  createActivityCategory,
  createActivity,
  createStatus, updateStatus, getStatusSources,
} from '@/api/mood'
import { createProperty } from '@/api/properties'
import { createHabit } from '@/api/habits'
import { uploadAttachment } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'
import { dbGetAll, dbPut } from '@/lib/db'

const PREDEFINED_MOODS = {
  1: { name: 'Rad',     color: '#5ebe6c', value: '255' },
  2: { name: 'Good',    color: '#9ecc6c', value: '200' },
  3: { name: 'Neutral', color: '#f0d060', value: '128' },
  4: { name: 'Bad',     color: '#f09060', value: '51'  },
  5: { name: 'Awful',   color: '#e05050', value: '1'   },
}

const MIME = {
  jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif',
  webp: 'image/webp', mp4: 'video/mp4', m4v: 'video/mp4', mov: 'video/quicktime',
  mp3: 'audio/mpeg', m4a: 'audio/mp4', ogg: 'audio/ogg', webm: 'video/webm',
}

const STEPS = [
  { key: 'moods',       label: 'Moods'          },
  { key: 'categories',  label: 'Categories'     },
  { key: 'activities',  label: 'Activities'     },
  { key: 'scales',      label: 'Custom scales'  },
  { key: 'goals',       label: 'Goals'          },
  { key: 'entries',     label: 'Entries'        },
  { key: 'attachments', label: 'Attachments'    },
]

const ZERO = () => ({ moods: 0, categories: 0, activities: 0, scales: 0, goals: 0, entries: 0, attachments: 0 })

const ks = useKeystoreStore()

const stage              = ref('pick')
const fileInput          = ref(null)
const parseError         = ref('')
const mapLoading         = ref(false)
const parsed             = ref(null)
const zipBuffer          = ref(null)
const zipIdx             = ref(null)
const existingMoods      = ref([])
const existingActivities = ref([])
const mappedMoods        = ref([])
const mappedActivities   = ref([])
const totals             = ref(ZERO())
const progress           = ref(ZERO())
const importError        = ref('')
const results            = ref(null)
const updateExisting     = ref(false)

const activeSteps = computed(() => STEPS.filter(s => totals.value[s.key] > 0))

function pct(key) {
  const t = totals.value[key]
  return t > 0 ? (progress.value[key] / t * 100).toFixed(1) + '%' : '0%'
}

function guessType(filename) {
  const ext = (filename || '').split('.').pop().toLowerCase()
  return MIME[ext] || 'application/octet-stream'
}

function resetPick() {
  stage.value = 'pick'
  parsed.value = null
  zipBuffer.value = null
  zipIdx.value = null
  parseError.value = ''
  importError.value = ''
  results.value = null
  existingMoods.value = []
  existingActivities.value = []
  mappedMoods.value = []
  mappedActivities.value = []
  mapLoading.value = false
  updateExisting.value = false
  if (fileInput.value) fileInput.value.value = ''
}

// Daylio goals: repeat_type 0=daily, 1=N×week, 2=specific weekdays (bitmask), 3=N×month
function mapGoalPeriod(repeatType, repeatValue) {
  if (repeatType === 0) return { period: 'daily', target_count: 1 }
  if (repeatType === 1) return { period: 'weekly', target_count: repeatValue || 1 }
  if (repeatType === 2) {
    let bits = repeatValue, count = 0
    while (bits > 0) { count += bits & 1; bits >>>= 1 }
    return { period: 'weekly', target_count: count || 1 }
  }
  if (repeatType === 3) return { period: 'monthly', target_count: repeatValue || 1 }
  return { period: 'weekly', target_count: 1 }
}

// ZIP parsing — reads the central directory (always has correct sizes, unlike local headers
// which may have compSz=0 when the data descriptor flag is set by Android ZipOutputStream).
function buildZipIndex(buffer) {
  const view  = new DataView(buffer)
  const bytes = new Uint8Array(buffer)

  // Find End of Central Directory record by scanning backwards for its signature.
  let eocd = -1
  for (let i = bytes.length - 22; i >= 0; i--) {
    if (view.getUint32(i, true) === 0x06054b50) { eocd = i; break }
  }
  if (eocd === -1) throw new Error('Not a valid ZIP file (EOCD not found)')

  const cdOffset = view.getUint32(eocd + 16, true)
  const cdCount  = view.getUint16(eocd + 10, true)

  const index = {}
  let pos = cdOffset
  for (let i = 0; i < cdCount; i++) {
    if (view.getUint32(pos, true) !== 0x02014b50) break
    const compression = view.getUint16(pos + 10, true)
    const compSz      = view.getUint32(pos + 20, true)
    const fnLen       = view.getUint16(pos + 28, true)
    const extraLen    = view.getUint16(pos + 30, true)
    const commentLen  = view.getUint16(pos + 32, true)
    const localOff    = view.getUint32(pos + 42, true)
    const filename    = new TextDecoder().decode(bytes.slice(pos + 46, pos + 46 + fnLen))
    // Resolve actual data start from local file header (its extra field may differ in length).
    const lfnLen      = view.getUint16(localOff + 26, true)
    const lextraLen   = view.getUint16(localOff + 28, true)
    const dataStart   = localOff + 30 + lfnLen + lextraLen
    index[filename]   = { compression, compSz, dataStart }
    pos += 46 + fnLen + extraLen + commentLen
  }
  return index
}

async function extractZipEntry(buffer, entry) {
  const bytes = new Uint8Array(buffer)
  const raw   = bytes.slice(entry.dataStart, entry.dataStart + entry.compSz)
  if (entry.compression === 0) return raw
  if (entry.compression === 8) {
    const ds = new DecompressionStream('deflate-raw')
    const inputStream = new ReadableStream({
      start(controller) { controller.enqueue(raw); controller.close() },
    })
    const reader = inputStream.pipeThrough(ds).getReader()
    const chunks = []
    for (;;) { const { done, value } = await reader.read(); if (done) break; chunks.push(value) }
    const out = new Uint8Array(chunks.reduce((n, c) => n + c.length, 0))
    let p = 0; for (const c of chunks) { out.set(c, p); p += c.length }
    return out
  }
  throw new Error(`Unsupported ZIP compression method: ${entry.compression}`)
}

function decodeBase64Json(b64) {
  const binary = atob(b64)
  const decoded = Uint8Array.from(binary, c => c.charCodeAt(0))
  return JSON.parse(new TextDecoder().decode(decoded))
}

async function parseDaylioFile(file) {
  const buf   = await file.arrayBuffer()
  const bytes = new Uint8Array(buf)
  if (bytes[0] === 0x50 && bytes[1] === 0x4b) {
    const index = buildZipIndex(buf)
    const entry = index['backup.daylio']
    if (!entry) throw new Error('backup.daylio not found inside the ZIP archive')
    const jsonBytes = await extractZipEntry(buf, entry)
    const text      = new TextDecoder().decode(jsonBytes)
    return { data: decodeBase64Json(text.trim()), buffer: buf, index }
  }
  const text = new TextDecoder().decode(bytes)
  return { data: decodeBase64Json(text.trim()), buffer: null, index: null }
}

async function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  parseError.value = ''
  mapLoading.value = true
  try {
    const { data, buffer, index } = await parseDaylioFile(file)
    if (!Array.isArray(data.dayEntries) || !Array.isArray(data.customMoods)) {
      throw new Error('Unrecognised format — expected a Daylio backup file.')
    }
    parsed.value    = data
    zipBuffer.value = buffer
    zipIdx.value    = index

    const [rawM, rawA] = await Promise.all([dbGetAll('moods'), dbGetAll('activities')])
    const [exMoods, exActs] = await Promise.all([ks.decryptAll(rawM), ks.decryptAll(rawA)])
    existingMoods.value      = exMoods
    existingActivities.value = exActs

    mappedMoods.value = data.customMoods
      .filter(dm => dm.state === 0)
      .map(dm => {
        const pre   = PREDEFINED_MOODS[dm.predefined_name_id] ?? { name: 'Unknown', color: '#888888', value: '128' }
        const name  = dm.custom_name || pre.name
        const match = exMoods.find(m => m.name?.toLowerCase() === name.toLowerCase())
        return { daylio: { id: dm.id, name, color: pre.color, value: pre.value }, matchId: match?.id ?? null }
      })

    mappedActivities.value = data.tags
      .filter(t => t.state === 0)
      .map(tag => {
        const match = exActs.find(a => a.name?.toLowerCase() === tag.name.toLowerCase())
        return { daylio: { id: tag.id, name: tag.name, groupId: tag.id_tag_group }, matchId: match?.id ?? null }
      })

    stage.value = 'map'
  } catch (err) {
    parseError.value = err.message || 'Could not read the file.'
  } finally {
    mapLoading.value = false
  }
}

function confirmMapping() {
  const data = parsed.value
  totals.value = {
    moods:       mappedMoods.value.length,
    categories:  (data.tag_groups ?? []).length,
    activities:  mappedActivities.value.length,
    scales:      (data.scales ?? []).filter(s => s.state === 0).length,
    goals:       (data.goals ?? []).filter(g => g.state === 0).length,
    entries:     data.dayEntries.length,
    attachments: zipIdx.value !== null ? (data.assets?.length ?? 0) : 0,
  }
  stage.value = 'preview'
}

async function startImport() {
  if (!ks.dataKey) {
    importError.value = 'Encryption key not ready — please wait and try again.'
    return
  }
  stage.value   = 'importing'
  importError.value = ''
  progress.value    = ZERO()
  const created = ZERO()
  const skipped = ZERO()
  const data    = parsed.value

  try {
    const [rawC, rawP, rawH] = await Promise.all([
      dbGetAll('activity_categories'),
      dbGetAll('properties'),
      dbGetAll('habits'),
    ])
    const [exCats, exProps, exHabits] = await Promise.all([
      ks.decryptAll(rawC),
      ks.decryptAll(rawP),
      ks.decryptAll(rawH),
    ])

    // 1. Moods — use confirmed mapping from map stage
    const moodIdMap = {}
    for (const m of mappedMoods.value) {
      if (m.matchId != null) {
        moodIdMap[m.daylio.id] = m.matchId
        skipped.moods++
      } else {
        const nm = await createMood({ encrypted_payload: await ks.encryptPayload({ name: m.daylio.name, icon: 'ph ph-smiley', color: m.daylio.color, value: m.daylio.value }) })
        await dbPut('moods', nm)
        moodIdMap[m.daylio.id] = nm.id
        created.moods++
      }
      progress.value.moods++
    }

    // 2. Categories
    const categoryIdMap = {}
    for (const tg of (data.tag_groups ?? [])) {
      const ex = exCats.find(c => c.name === tg.name)
      if (ex) {
        categoryIdMap[tg.id] = ex.id; skipped.categories++
      } else {
        const c = await createActivityCategory({ encrypted_payload: await ks.encryptPayload({ name: tg.name, icon: 'ph ph-tag' }) })
        await dbPut('activity_categories', c)
        categoryIdMap[tg.id] = c.id; created.categories++
      }
      progress.value.categories++
    }

    // 3. Activities — use confirmed mapping from map stage
    const activityIdMap = {}
    for (const a of mappedActivities.value) {
      if (a.matchId != null) {
        activityIdMap[a.daylio.id] = a.matchId
        skipped.activities++
      } else {
        const payload = { encrypted_payload: await ks.encryptPayload({ name: a.daylio.name, icon: 'ph ph-circle' }) }
        const catId = categoryIdMap[a.daylio.groupId] ?? null
        if (catId != null) payload.category = catId
        const act = await createActivity(payload)
        await dbPut('activities', act)
        activityIdMap[a.daylio.id] = act.id
        created.activities++
      }
      progress.value.activities++
    }

    // 4. Scales → Custom properties
    const scaleIdMap = {}
    for (const scale of (data.scales ?? [])) {
      if (scale.state !== 0) continue
      const ex = exProps.find(p => p.name === scale.name)
      if (ex) {
        scaleIdMap[scale.id] = ex.id; skipped.scales++
      } else {
        const minVal = scale.min_value ?? scale.min_val ?? 0
        const maxVal = scale.max_value ?? scale.max_val ?? 10
        const prop = await createProperty({ encrypted_payload: await ks.encryptPayload({ name: scale.name, type: 'scale', min_val: minVal, max_val: maxVal }) })
        await dbPut('properties', prop)
        scaleIdMap[scale.id] = prop.id; created.scales++
      }
      progress.value.scales++
    }

    // 5. Goals → Habits
    for (const goal of (data.goals ?? [])) {
      if (goal.state !== 0) continue
      const actId = activityIdMap[goal.id_tag]
      if (actId == null) { skipped.goals++; progress.value.goals++; continue }
      const ex = exHabits.find(h => String(h.activity_id) === String(actId))
      if (ex) {
        skipped.goals++
      } else {
        const { period, target_count } = mapGoalPeriod(goal.repeat_type, goal.repeat_value)
        const habit = await createHabit({ encrypted_payload: await ks.encryptPayload({ activity_id: actId, goal: { target_count, period } }) })
        await dbPut('habits', habit)
        created.goals++
      }
      progress.value.goals++
    }

    // 6. Entries
    const sourcesRaw = await getStatusSources('daylio:')
    const importedSources = new Map(
      sourcesRaw.map(s => typeof s === 'string' ? [s, null] : [s.source, s.id])
    )
    const assetById = Object.fromEntries((data.assets ?? []).map(a => [a.id, a]))
    const pendingAttachments = []

    // Build checksum→entry map using only the basename so folder-prefixed
    // asset paths (e.g. "assets/CHECKSUM") resolve correctly.
    const zipByChecksum = {}
    if (zipIdx.value) {
      for (const [path, ent] of Object.entries(zipIdx.value)) {
        if (path === 'backup.daylio') continue
        zipByChecksum[path.split('/').pop()] = ent
      }
    }

    for (const entry of data.dayEntries) {
      const source = `daylio:${entry.datetime}`
      const moodId = moodIdMap[entry.mood]
      const actIds = (entry.tags ?? []).filter(t => activityIdMap[t] != null).map(t => activityIdMap[t])
      const toEncrypt = {}
      if (moodId != null)  toEncrypt.mood_id      = String(moodId)
      if (actIds.length)   toEncrypt.activity_ids = JSON.stringify(actIds)
      if (entry.note)      toEncrypt.text          = entry.note

      if ((entry.scaleValues ?? []).length) {
        const props = {}
        for (const sv of entry.scaleValues) {
          const propId = scaleIdMap[sv.scale_id]
          if (propId != null) props[String(propId)] = sv.value
        }
        if (Object.keys(props).length) toEncrypt.properties = props
      }

      if (importedSources.has(source)) {
        const existingId = importedSources.get(source)
        if (updateExisting.value) {
          await updateStatus(existingId, { encrypted_payload: await ks.encryptPayload(toEncrypt) })
          created.entries++
        } else {
          skipped.entries++
        }
        progress.value.entries++
        if ((entry.assets ?? []).length && zipIdx.value && existingId != null) {
          for (const assetId of entry.assets) {
            const asset = assetById[assetId]
            if (asset) pendingAttachments.push({ statusId: existingId, asset })
          }
        }
        continue
      }

      const status = await createStatus({
        encrypted_payload: await ks.encryptPayload(toEncrypt),
        timestamp: new Date(entry.datetime).toISOString(),
        source,
      })
      created.entries++
      progress.value.entries++

      if ((entry.assets ?? []).length && zipIdx.value) {
        for (const assetId of entry.assets) {
          const asset = assetById[assetId]
          if (asset) pendingAttachments.push({ statusId: status.id, asset })
        }
      }
    }

    // 7. Attachments
    for (const { statusId, asset } of pendingAttachments) {
      const zipEntry = zipByChecksum[asset.checksum]
      if (!zipEntry) { skipped.attachments++; progress.value.attachments++; continue }
      try {
        const bytes = await extractZipEntry(zipBuffer.value, zipEntry)
        let name = asset.checksum
        try { name = JSON.parse(asset.android_metadata || '{}').Name || name } catch {}
        const file = new File([bytes], name, { type: guessType(name) })
        await uploadAttachment(statusId, file, ks.dataKey, false, `daylio:${asset.checksum}`)
        created.attachments++
      } catch {
        skipped.attachments++
      }
      progress.value.attachments++
    }

    results.value = { created, skipped }
    stage.value = 'done'
  } catch (err) {
    importError.value = err.message || 'Import failed — some items may not have been created.'
    results.value = { created, skipped }
    stage.value = 'done'
  }
}
</script>
