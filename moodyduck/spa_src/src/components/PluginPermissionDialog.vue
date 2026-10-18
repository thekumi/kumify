<template>
    <div v-if="store.pending"
         class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-5 space-y-4">
            <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center shrink-0 mt-0.5">
                    <i class="ph ph-lock-key text-amber-600 text-xl"></i>
                </div>
                <div>
                    <p class="font-semibold text-stone-800">Permission request</p>
                    <p class="text-sm text-stone-500 mt-0.5">
                        <span class="font-medium text-stone-700">{{ store.pending.pluginName }}</span>
                        wants to read and write your encrypted data.
                    </p>
                </div>
            </div>
            <label class="flex items-center gap-2.5 text-sm text-stone-600 cursor-pointer select-none">
                <input type="checkbox"
                       v-model="remember"
                       class="rounded border-stone-300 text-sky-600 focus:ring-sky-400" />
                Remember my choice
            </label>
            <div class="flex gap-3 pt-1">
                <button @click="deny"
                        class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-semibold hover:bg-stone-50 transition-colors">
                    Deny
                </button>
                <button @click="grant"
                        class="flex-1 py-2.5 rounded-xl bg-sky-600 text-white text-sm font-semibold hover:bg-sky-700 transition-colors">
                    Allow
                </button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { usePluginPermissionsStore } from '@/stores/pluginPermissions'

const store = usePluginPermissionsStore()
const remember = ref(false)

function grant() {
  store.pending.grant(remember.value)
  remember.value = false
}

function deny() {
  store.pending.deny(remember.value)
  remember.value = false
}
</script>
