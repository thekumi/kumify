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
          <input v-model="form.name" type="text" required placeholder="Full name"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Nickname <span class="font-normal">(optional)</span></label>
          <input v-model="form.nickname" type="text" placeholder="How you call them"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Relationship</label>
          <input v-model="form.relationship" type="text" placeholder="e.g. Partner, Parent, Friend"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Phone</label>
          <input v-model="form.phone" type="tel" placeholder="+1 555 000 0000"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Email</label>
          <input v-model="form.email" type="email" placeholder="them@example.com"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Birthday</label>
          <input v-model="form.birthday" type="date"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Address</label>
          <textarea v-model="form.address" rows="2" placeholder="Street, city, country"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Notes</label>
          <textarea v-model="form.notes" rows="3" placeholder="Anything to remember…"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-violet-400 text-stone-800 bg-stone-50 text-sm resize-none"></textarea>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <label class="flex items-center gap-3 cursor-pointer">
          <div class="relative">
            <input v-model="form.emergency_contact" type="checkbox" class="sr-only peer" />
            <div class="w-10 h-6 bg-stone-200 peer-checked:bg-red-500 rounded-full transition-colors"></div>
            <div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4"></div>
          </div>
          <div>
            <p class="text-sm font-semibold text-stone-700">Emergency contact</p>
            <p class="text-xs text-stone-400">Shown on the lock screen in emergencies</p>
          </div>
        </label>
      </div>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Add person') }}
      </button>

      <button v-if="id" type="button" @click="remove"
        class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Remove person
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getPerson, createPerson, updatePerson, deletePerson } from '@/api/people'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', nickname: '', relationship: '', phone: '', email: '', birthday: '', address: '', notes: '', emergency_contact: false })
const loading = ref(!!id)
const saving = ref(false)
const error = ref('')

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) await updatePerson(id, form.value)
    else await createPerson(form.value)
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
    const p = await getPerson(id)
    form.value = {
      name: p.name ?? '',
      nickname: p.nickname ?? '',
      relationship: p.relationship ?? '',
      phone: p.phone ?? '',
      email: p.email ?? '',
      birthday: p.birthday ?? '',
      address: p.address ?? '',
      notes: p.notes ?? '',
      emergency_contact: p.emergency_contact ?? false,
    }
    loading.value = false
  }
})
</script>
