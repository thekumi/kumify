<template>
  <div class="min-h-screen bg-clay-50 flex flex-col items-center justify-center px-6 py-12">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-clay-100 rounded-3xl mb-4">
          <DuckIcon bg="#faeade" class="w-9 h-9 text-clay-600"/>
        </div>
        <h1 class="text-3xl font-bold text-stone-800">MoodyDuck</h1>
        <p class="text-stone-500 mt-1 text-sm">Sign in to your account</p>
      </div>

      <form @submit.prevent="submit" class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-stone-700 mb-1">Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            autocomplete="username"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-stone-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 px-4 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors"
        >
          <span v-if="loading">Signing in…</span>
          <span v-else>Sign in</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import DuckIcon from '@/components/DuckIcon.vue'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await login(form.value.username, form.value.password)
    await auth.init()
    router.push('/')
  } catch (e) {
    error.value = e.data?.non_field_errors?.[0] ?? 'Invalid credentials.'
  } finally {
    loading.value = false
  }
}
</script>
