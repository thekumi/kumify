<template>
    <div class="min-h-screen bg-clay-50 flex flex-col items-center justify-center px-6 py-12">
        <div class="w-full max-w-sm">
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-clay-100 rounded-3xl mb-4">
                    <DuckIcon bg="#faeade" class="w-9 h-9 text-clay-600" />
                </div>
                <h1 class="text-3xl font-bold text-stone-800">MoodyDuck</h1>
                <p class="text-stone-500 mt-1 text-sm">Create an account</p>
            </div>
            <!-- Registration closed -->
            <div v-if="serverInfo && !serverInfo.registration_open"
                 class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6 text-center text-stone-500 text-sm">
                Registration is not open on this server.
            </div>
            <!-- Success: pending -->
            <div v-else-if="result === 'pending'"
                 class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6 text-center space-y-2">
                <i class="ph ph-hourglass text-clay-400 text-4xl"></i>
                <p class="font-semibold text-stone-700">Registration submitted</p>
                <p class="text-sm text-stone-500">
                    Your account is pending approval by a server administrator. You'll be able to sign in once it's approved.
                </p>
                <RouterLink to="/login" class="block mt-4 text-sm text-clay-600 font-medium hover:underline">
                Back to sign in
                </RouterLink>
            </div>
            <!-- Success: active -->
            <div v-else-if="result === 'active'"
                 class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6 text-center space-y-2">
                <i class="ph ph-check-circle text-green-500 text-4xl"></i>
                <p class="font-semibold text-stone-700">Account created</p>
                <p class="text-sm text-stone-500">You can now sign in.</p>
                <RouterLink to="/login" class="block mt-4 text-sm text-clay-600 font-medium hover:underline">
                Sign in
                </RouterLink>
            </div>
            <!-- Form -->
            <form v-else-if="serverInfo"
                  @submit.prevent="submit"
                  class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6 space-y-4">
                <div>
                    <label class="block text-sm font-medium text-stone-700 mb-1">Username</label>
                    <input v-model="form.username"
                           type="text"
                           required
                           autocomplete="username"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50"
                           :class="{ 'border-red-300': errors.username }" />
                    <p v-if="errors.username" class="text-xs text-red-600 mt-1">{{ errors.username[0] }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-stone-700 mb-1">Email <span class="text-stone-400 font-normal">(optional)</span></label>
                    <input v-model="form.email"
                           type="email"
                           autocomplete="email"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50" />
                </div>
                <div>
                    <label class="block text-sm font-medium text-stone-700 mb-1">Password</label>
                    <input v-model="form.password"
                           type="password"
                           required
                           autocomplete="new-password"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50"
                           :class="{ 'border-red-300': errors.password }" />
                    <p v-if="errors.password" class="text-xs text-red-600 mt-1">{{ errors.password[0] }}</p>
                </div>
                <div v-if="serverInfo.require_reason">
                    <label class="block text-sm font-medium text-stone-700 mb-1">Why do you want to join?</label>
                    <textarea v-model="form.reason"
                              rows="3"
                              required
                              class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 focus:border-transparent text-stone-800 bg-stone-50 resize-none text-sm"
                              :class="{ 'border-red-300': errors.reason }"></textarea>
                    <p v-if="errors.reason" class="text-xs text-red-600 mt-1">{{ errors.reason[0] }}</p>
                </div>
                <p v-if="serverInfo.require_approval"
                   class="text-xs text-stone-400 bg-stone-50 rounded-xl px-3 py-2">
                    Registration requires admin approval. You'll need to wait before you can sign in.
                </p>
                <p v-if="errors.detail"
                   class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ errors.detail }}</p>
                <button type="submit"
                        :disabled="loading"
                        class="w-full py-3 px-4 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
                    <span v-if="loading">Creating account…</span>
                    <span v-else>Create account</span>
                </button>
            </form>
            <p v-if="!result" class="text-center text-sm text-stone-500 mt-4">
                Already have an account?
                <RouterLink to="/login" class="text-clay-600 font-medium hover:underline">Sign in</RouterLink>
            </p>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getServerInfo, register } from '@/api/auth'
import DuckIcon from '@/components/DuckIcon.vue'

const serverInfo = ref(null)
const form = ref({ username: '', email: '', password: '', reason: '' })
const loading = ref(false)
const errors = ref({})
const result = ref(null)

onMounted(async () => {
  try { serverInfo.value = await getServerInfo() } catch { /* server unreachable */ }
})

async function submit() {
  loading.value = true
  errors.value = {}
  try {
    const data = await register(form.value)
    result.value = data.status
  } catch (e) {
    errors.value = e.data ?? {}
  } finally {
    loading.value = false
  }
}
</script>
