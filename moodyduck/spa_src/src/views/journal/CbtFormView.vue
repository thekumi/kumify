<template>
  <div class="pb-nav">
    <TopBar :title="id ? 'Edit Thought Record' : 'New Thought Record'" :back="true" />

    <form @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Title <span class="font-normal">(optional)</span></label>
          <input v-model="form.title" type="text" placeholder="Brief label…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Situation</label>
          <textarea v-model="form.situation" rows="3" placeholder="What happened? Where were you?"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm resize-none leading-relaxed"></textarea>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Automatic thoughts</label>
          <textarea v-model="form.thoughts" rows="4" placeholder="What went through your mind?"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-purple-400 text-stone-800 bg-stone-50 text-sm resize-none leading-relaxed"></textarea>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Save record') }}
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
import { getRecord, createRecord, updateRecord } from '@/api/cbt'
import { useKeystoreStore } from '@/stores/keystore'
import { useOfflineStore } from '@/stores/offline'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const offline = useOfflineStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ title: '', situation: '', thoughts: '' })
const saving = ref(false)
const error = ref('')
let rawRecord = null
let hiddenFields = { pro_facts: null, con_facts: null, realistic: null, outcome: null }

const ALL_ENCRYPTED_FIELDS = ['title', 'situation', 'thoughts', 'pro_facts', 'con_facts', 'realistic', 'outcome']

async function fillForm(r) {
  const dec = await ks.decrypt(r)
  form.value = { title: dec.title ?? '', situation: dec.situation ?? '', thoughts: dec.thoughts ?? '' }
  hiddenFields = { pro_facts: dec.pro_facts ?? null, con_facts: dec.con_facts ?? null, realistic: dec.realistic ?? null, outcome: dec.outcome ?? null }
}

watch(() => ks.dataKey, async (key) => { if (key && rawRecord) await fillForm(rawRecord) })

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) {
      const result = await saveEncrypted(updateRecord, id, { ...form.value, ...hiddenFields }, ALL_ENCRYPTED_FIELDS, rawRecord, ks)
      router.push(`/journal/cbt/${result.id}`)
    } else if (!navigator.onLine) {
      await offline.enqueue({ endpoint: '/cbt/records/', payload: form.value })
      router.push('/journal/cbt')
    } else {
      try {
        const result = await createRecord(form.value)
        router.push(`/journal/cbt/${result.id}`)
      } catch (e) {
        if (!(e instanceof TypeError)) throw e
        await offline.enqueue({ endpoint: '/cbt/records/', payload: form.value })
        router.push('/journal/cbt')
      }
    }
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

onMounted(async () => {
  if (id) {
    rawRecord = await getRecord(id)
    await fillForm(rawRecord)
  }
})
</script>
