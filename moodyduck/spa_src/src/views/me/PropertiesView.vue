<template>
  <div class="pb-nav">
    <TopBar title="Custom Properties" :back="true">
      <template #actions>
        <button @click="openNew" class="w-8 h-8 flex items-center justify-center rounded-full bg-violet-100 hover:bg-violet-200 transition-colors">
          <i class="ph ph-plus text-violet-700"></i>
        </button>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!properties.length" class="flex flex-col items-center py-20 text-center px-6">
      <i class="ph ph-sliders text-6xl text-stone-300 mb-4"></i>
      <p class="text-stone-500 font-medium">No custom properties yet</p>
      <p class="text-sm text-stone-400 mt-1">Track anything extra on your mood entries</p>
      <button @click="openNew" class="mt-4 px-5 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-medium hover:bg-violet-700 transition-colors">
        Add property
      </button>
    </div>

    <ul v-else class="mx-4 mt-4 space-y-2">
      <li v-for="p in properties" :key="p.id" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-violet-50">
          <i :class="p.type === 'boolean' ? 'ph ph-toggle-right' : 'ph ph-sliders-horizontal'" class="text-xl text-violet-500"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="font-medium text-stone-800 truncate">{{ p.name || '—' }}</p>
          <p class="text-xs text-stone-400">
            {{ p.type === 'boolean' ? 'Yes / No' : `Scale ${p.min_val}–${p.max_val}` }}
          </p>
        </div>
        <button @click="openEdit(p)" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors shrink-0">
          <i class="ph ph-pencil-simple text-stone-400"></i>
        </button>
      </li>
    </ul>

    <div v-if="sheet" class="fixed inset-0 bg-black/30 z-50 flex items-end" @click.self="sheet = null">
      <div class="bg-white w-full rounded-t-3xl p-6 space-y-4">
        <h2 class="text-lg font-semibold text-stone-800">{{ sheet.id ? 'Edit Property' : 'New Property' }}</h2>

        <input v-model="sheet.name" type="text" placeholder="Property name" autofocus
          class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />

        <div v-if="!sheet.id" class="flex gap-0.5 bg-stone-100 rounded-xl p-0.5">
          <button v-for="t in [['scale','Scale'],['boolean','Yes / No']]" :key="t[0]"
            @click="sheet.propType = t[0]"
            class="flex-1 text-sm py-2 rounded-lg font-medium transition-colors"
            :class="sheet.propType === t[0] ? 'bg-white shadow-sm text-stone-800' : 'text-stone-400'">
            {{ t[1] }}
          </button>
        </div>
        <p v-else class="text-xs text-stone-400">Type: {{ sheet.propType === 'boolean' ? 'Yes / No' : 'Scale' }}</p>

        <div v-if="sheet.propType === 'scale'" class="flex items-center gap-3">
          <div class="flex-1">
            <label class="text-xs text-stone-400 block mb-1">Min</label>
            <input type="number" v-model.number="sheet.minVal"
              class="w-full px-3 py-2 rounded-xl border border-stone-200 text-sm text-stone-800 bg-stone-50 focus:outline-none focus:ring-2 focus:ring-violet-400" />
          </div>
          <div class="flex-1">
            <label class="text-xs text-stone-400 block mb-1">Max</label>
            <input type="number" v-model.number="sheet.maxVal"
              class="w-full px-3 py-2 rounded-xl border border-stone-200 text-sm text-stone-800 bg-stone-50 focus:outline-none focus:ring-2 focus:ring-violet-400" />
          </div>
        </div>

        <p v-if="sheetError" class="text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ sheetError }}</p>

        <div class="flex gap-3">
          <button v-if="sheet.id" @click="removeProperty(sheet)" type="button"
            class="py-3 px-4 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
            Delete
          </button>
          <button @click="sheet = null" class="flex-1 py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
          <button @click="saveProperty" :disabled="!sheet.name || sheetSaving"
            class="flex-1 py-3 rounded-xl bg-violet-600 text-white text-sm font-medium hover:bg-violet-700 transition-colors disabled:opacity-50">
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
import { getProperties, createProperty, updateProperty, deleteProperty } from '@/api/properties'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const properties = ref([])
const raw = ref([])
const loading = ref(true)
const sheet = ref(null)
const sheetSaving = ref(false)
const sheetError = ref('')

async function applyDecryption() { properties.value = await ks.decryptAll(raw.value) }
watch(() => ks.dataKey, (key) => { if (key) applyDecryption() })

function openNew() {
  sheet.value = { name: '', propType: 'scale', minVal: 1, maxVal: 10 }
  sheetError.value = ''
}

function openEdit(p) {
  const rawProp = raw.value.find(r => r.id === p.id)
  sheet.value = {
    id: p.id, _raw: rawProp,
    name: p.name ?? '',
    propType: p.type ?? 'scale',
    minVal: p.min_val ?? 1,
    maxVal: p.max_val ?? 10,
  }
  sheetError.value = ''
}

async function saveProperty() {
  if (!sheet.value.name) return
  sheetSaving.value = true; sheetError.value = ''
  try {
    const payload = { name: sheet.value.name, type: sheet.value.propType }
    if (sheet.value.propType === 'scale') {
      payload.min_val = sheet.value.minVal
      payload.max_val = sheet.value.maxVal
    }
    if (sheet.value.id) {
      await saveEncrypted(updateProperty, sheet.value.id, payload, Object.keys(payload), sheet.value._raw, ks)
    } else {
      await createProperty({ encrypted_payload: await ks.encryptPayload(payload) })
    }
    sheet.value = null
    raw.value = await getProperties()
    await applyDecryption()
  } catch { sheetError.value = 'Could not save.' }
  finally { sheetSaving.value = false }
}

async function removeProperty(p) {
  if (!confirm('Delete this property?')) return
  await deleteProperty(p.id)
  sheet.value = null
  raw.value = await getProperties()
  await applyDecryption()
}

onMounted(async () => {
  raw.value = await getProperties()
  await applyDecryption()
  loading.value = false
})
</script>
