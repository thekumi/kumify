<template>
    <div class="pb-nav">
        <TopBar :title="id ? 'Edit Person' : 'New Person'" :back="true" />
        <div v-if="loading" class="flex justify-center py-16">
            <div class="w-8 h-8 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>
        </div>
        <form v-else @submit.prevent="save" class="px-4 py-4 space-y-3">
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name <span class="text-red-400">*</span></label>
                    <input v-model="form.name"
                           type="text"
                           required
                           placeholder="Full name"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Nickname <span class="font-normal">(optional)</span></label>
                    <input v-model="form.nickname"
                           type="text"
                           placeholder="How you call them"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Relationship</label>
                    <input v-model="form.relationship"
                           type="text"
                           placeholder="e.g. Partner, Parent, Friend"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
            </div>
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Phone</label>
                    <div v-for="(_, i) in form.phones" :key="i" class="flex gap-2 mb-2">
                        <input v-model="form.phones[i]"
                               type="tel"
                               placeholder="+1 555 000 0000"
                               class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                        <button v-if="form.phones.length > 1"
                                type="button"
                                @click="form.phones.splice(i, 1)"
                                class="w-10 flex-none flex items-center justify-center rounded-xl border border-stone-200 text-stone-400 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors">
                            <i class="ph ph-minus text-sm"></i>
                        </button>
                    </div>
                    <button type="button"
                            @click="form.phones.push('')"
                            class="text-xs text-violet-500 hover:text-violet-600 font-medium flex items-center gap-1">
                        <i class="ph ph-plus text-xs"></i> Add phone
                    </button>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Email</label>
                    <div v-for="(_, i) in form.emails" :key="i" class="flex gap-2 mb-2">
                        <input v-model="form.emails[i]"
                               type="email"
                               placeholder="them@example.com"
                               class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                        <button v-if="form.emails.length > 1"
                                type="button"
                                @click="form.emails.splice(i, 1)"
                                class="w-10 flex-none flex items-center justify-center rounded-xl border border-stone-200 text-stone-400 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors">
                            <i class="ph ph-minus text-sm"></i>
                        </button>
                    </div>
                    <button type="button"
                            @click="form.emails.push('')"
                            class="text-xs text-violet-500 hover:text-violet-600 font-medium flex items-center gap-1">
                        <i class="ph ph-plus text-xs"></i> Add email
                    </button>
                </div>
                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-sm font-semibold text-stone-500">Birthday</label>
                        <label class="flex items-center gap-1.5 cursor-pointer select-none">
                            <input v-model="birthdayNoYear"
                                   type="checkbox"
                                   class="rounded"
                                   @change="onBirthdayModeChange" />
                            <span class="text-xs text-stone-400">Year unknown</span>
                        </label>
                    </div>
                    <input v-if="!birthdayNoYear"
                           v-model="form.birthday"
                           type="date"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-else
                           v-model="form.birthday_monthday"
                           type="text"
                           placeholder="MM-DD"
                           maxlength="5"
                           pattern="\d{2}-\d{2}"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Address</label>
                    <div v-for="(_, i) in form.addresses" :key="i" class="flex gap-2 mb-2">
                        <textarea v-model="form.addresses[i]"
                                  rows="2"
                                  placeholder="Street, city, country"
                                  class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
                        <button v-if="form.addresses.length > 1"
                                type="button"
                                @click="form.addresses.splice(i, 1)"
                                class="w-10 flex-none flex items-center justify-center rounded-xl border border-stone-200 text-stone-400 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors self-start mt-0.5">
                            <i class="ph ph-minus text-sm"></i>
                        </button>
                    </div>
                    <button type="button"
                            @click="form.addresses.push('')"
                            class="text-xs text-violet-500 hover:text-violet-600 font-medium flex items-center gap-1">
                        <i class="ph ph-plus text-xs"></i> Add address
                    </button>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Organisation</label>
                    <input v-model="form.organization"
                           type="text"
                           placeholder="Company or organisation"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Title</label>
                    <input v-model="form.title"
                           type="text"
                           placeholder="Job title"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Website</label>
                    <div v-for="(_, i) in form.websites" :key="i" class="flex gap-2 mb-2">
                        <input v-model="form.websites[i]"
                               type="url"
                               placeholder="https://example.com"
                               class="flex-1 px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                        <button v-if="form.websites.length > 1"
                                type="button"
                                @click="form.websites.splice(i, 1)"
                                class="w-10 flex-none flex items-center justify-center rounded-xl border border-stone-200 text-stone-400 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors">
                            <i class="ph ph-minus text-sm"></i>
                        </button>
                    </div>
                    <button type="button"
                            @click="form.websites.push('')"
                            class="text-xs text-violet-500 hover:text-violet-600 font-medium flex items-center gap-1">
                        <i class="ph ph-plus text-xs"></i> Add website
                    </button>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Notes</label>
                    <textarea v-model="form.notes"
                              rows="3"
                              placeholder="Anything to remember…"
                              class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Last contact</label>
                    <input v-model="form.last_contact"
                           type="date"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
            </div>
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                <label class="flex items-center gap-3 cursor-pointer">
                    <div class="relative">
                        <input v-model="form.emergency_contact" type="checkbox" class="sr-only peer" />
                        <div class="w-10 h-6 bg-stone-200 peer-checked:bg-red-500 rounded-full transition-colors"></div>
                        <div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4">
                        </div>
                    </div>
                    <div>
                        <p class="text-sm font-semibold text-stone-700">Emergency contact</p>
                        <p class="text-xs text-stone-400">Shown on the lock screen in emergencies</p>
                    </div>
                </label>
            </div>
            <p v-if="error"
               class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>
            <button type="submit"
                    :disabled="saving"
                    class="w-full py-3.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
                {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add person') }}
            </button>
            <button v-if="id"
                    type="button"
                    @click="remove"
                    class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                Remove person
            </button>
        </form>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getPerson, createPerson, updatePerson, deletePerson } from '@/api/people'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', nickname: '', relationship: '', phones: [''], emails: [''], birthday: '', birthday_monthday: '', addresses: [], notes: '', organization: '', title: '', websites: [], last_contact: '', emergency_contact: false })
const loading = ref(!!id)
const saving = ref(false)
const error = ref('')
let rawPerson = null

const ENCRYPTED_FIELDS = ['name', 'nickname', 'birthday', 'birthday_monthday', 'emails', 'phones', 'relationship', 'addresses', 'notes', 'organization', 'title', 'websites', 'last_contact']

const birthdayNoYear = computed({
  get: () => !!form.value.birthday_monthday && !form.value.birthday,
  set: (v) => {
    if (!v) form.value.birthday_monthday = ''
    else form.value.birthday = ''
  },
})

function onBirthdayModeChange() {
  if (birthdayNoYear.value) form.value.birthday = ''
  else form.value.birthday_monthday = ''
}

function toArray(v, fallback = []) {
  if (Array.isArray(v)) return v.length ? v : fallback
  if (typeof v === 'string' && v) return [v]
  return fallback
}

async function fillForm(p) {
  const dec = await ks.decrypt(p)
  form.value = {
    name: dec.name ?? '',
    nickname: dec.nickname ?? '',
    relationship: dec.relationship ?? '',
    phones: toArray(dec.phones ?? dec.phone, ['']),
    emails: toArray(dec.emails ?? dec.email, ['']),
    birthday: dec.birthday ?? '',
    birthday_monthday: dec.birthday_monthday ?? '',
    addresses: toArray(dec.addresses ?? dec.address),
    notes: dec.notes ?? '',
    organization: dec.organization ?? '',
    title: dec.title ?? '',
    websites: toArray(dec.websites ?? dec.website),
    last_contact: dec.last_contact ?? '',
    emergency_contact: p.emergency_contact ?? false,
  }
}

watch(() => ks.dataKey, async (key) => { if (key && rawPerson) await fillForm(rawPerson) })

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) {
      await saveEncrypted(updatePerson, id, { ...form.value }, ENCRYPTED_FIELDS, rawPerson, ks)
    } else {
      const toEncrypt = {}
      for (const field of ENCRYPTED_FIELDS) {
        const v = form.value[field]
        const filled = Array.isArray(v) ? v.filter(Boolean) : v
        if (filled !== null && filled !== undefined && filled !== '' && !(Array.isArray(filled) && !filled.length)) {
          toEncrypt[field] = filled
        }
      }
      const encrypted_payload = await ks.encryptPayload(toEncrypt)
      await createPerson({ encrypted_payload, emergency_contact: form.value.emergency_contact })
    }
    router.push('/people')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Remove this person?')) return
  await deletePerson(id)
  router.push('/people')
}

onMounted(async () => {
  if (id) {
    rawPerson = await getPerson(id)
    await fillForm(rawPerson)
    loading.value = false
  }
})
</script>
