<template>
  <div class="pb-nav">
    <TopBar title="Profile" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <form v-else @submit.prevent="save" class="px-4 py-4 space-y-3">
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Display name</label>
          <input v-model="form.display_name" type="text" placeholder="How should we call you?"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Email address</label>
          <input v-model="form.email" type="email" placeholder="you@example.com"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Legal name</label>
          <input v-model="form.legal_name" type="text" placeholder="Full legal name"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Date of birth</label>
          <input v-model="form.date_of_birth" type="date"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Phone</label>
          <input v-model="form.phone" type="tel" placeholder="+1 555 000 0000"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
        <div>
          <label class="text-sm font-semibold text-stone-500 block mb-1.5">Time zone</label>
          <input v-model="form.timezone" type="text" placeholder="e.g. Europe/Vienna"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
        </div>
      </div>

      <p v-if="saved" class="text-sm text-green-700 bg-green-50 rounded-xl px-4 py-3">Saved!</p>
      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>

      <button type="submit" :disabled="saving"
        class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getProfile, updateProfile } from '@/api/profile'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const form = ref({ display_name: '', email: '', legal_name: '', date_of_birth: '', phone: '', timezone: '' })
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

async function save() {
  saving.value = true; error.value = ''; saved.value = false
  try {
    await updateProfile(form.value)
    await auth.init()
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

onMounted(async () => {
  const p = await getProfile()
  form.value = {
    display_name: p.display_name ?? '',
    email: p.email ?? '',
    legal_name: p.legal_name ?? '',
    date_of_birth: p.date_of_birth ?? '',
    phone: p.phone ?? '',
    timezone: p.timezone ?? '',
  }
  loading.value = false
})
</script>
