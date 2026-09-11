<template>
  <div class="pb-nav">
    <TopBar title="Privacy & Security" :back="true" />

    <div class="px-4 py-4 space-y-4">

      <!-- Lock PIN -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
        <div class="flex items-center gap-2 mb-1">
          <i class="ph ph-lock text-stone-400 text-lg"></i>
          <p class="text-sm font-semibold text-stone-700">Lock PIN</p>
          <span class="ml-auto text-xs font-medium px-2 py-0.5 rounded-full"
            :class="ks.lockConfigured ? 'bg-green-100 text-green-700' : 'bg-stone-100 text-stone-500'">
            {{ ks.lockConfigured ? 'Active' : 'Not set' }}
          </span>
        </div>

        <p class="text-xs text-stone-400 leading-relaxed">
          When set, your encryption key is wrapped with this PIN and the raw key is never stored on
          disk. Locking the app requires this PIN to decrypt anything.
        </p>

        <!-- Set PIN form -->
        <template v-if="mode === 'set'">
          <input v-model="newPin" type="password" placeholder="New PIN or passphrase (min 4 chars)"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
          <input v-model="confirmPin" type="password" placeholder="Confirm PIN"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
          <p v-if="formError" class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
          <div class="flex gap-2">
            <button @click="mode = 'idle'" class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
            <button @click="doSetPin" :disabled="busy" class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
              {{ busy ? 'Saving…' : 'Set PIN' }}
            </button>
          </div>
        </template>

        <!-- Change PIN form -->
        <template v-else-if="mode === 'change'">
          <input v-model="oldPin" type="password" placeholder="Current PIN"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
          <input v-model="newPin" type="password" placeholder="New PIN (min 4 chars)"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
          <input v-model="confirmPin" type="password" placeholder="Confirm new PIN"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
          <p v-if="formError" class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
          <div class="flex gap-2">
            <button @click="mode = 'idle'" class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
            <button @click="doChangePin" :disabled="busy" class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
              {{ busy ? 'Saving…' : 'Change PIN' }}
            </button>
          </div>
        </template>

        <!-- Remove PIN form -->
        <template v-else-if="mode === 'remove'">
          <p class="text-xs text-amber-700 bg-amber-50 rounded-xl px-3 py-2">
            This will store your encryption key unprotected in the browser. Anyone with access to this device could potentially read it.
          </p>
          <input v-model="oldPin" type="password" placeholder="Current PIN to confirm"
            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-red-400 text-stone-800 bg-stone-50 text-sm" />
          <p v-if="formError" class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
          <div class="flex gap-2">
            <button @click="mode = 'idle'" class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
            <button @click="doRemovePin" :disabled="busy || !oldPin" class="flex-1 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
              {{ busy ? 'Removing…' : 'Remove PIN' }}
            </button>
          </div>
        </template>

        <!-- Idle state buttons -->
        <template v-else>
          <button v-if="!ks.lockConfigured" @click="openSet"
            class="w-full py-2.5 bg-clay-600 hover:bg-clay-700 text-white text-sm font-semibold rounded-xl transition-colors">
            Set Lock PIN
          </button>
          <div v-else class="flex gap-2">
            <button @click="openChange" class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Change PIN</button>
            <button @click="openRemove" class="flex-1 py-2.5 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">Remove PIN</button>
          </div>
        </template>
      </div>

      <!-- Auto-lock -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <div class="flex items-center gap-2 mb-1">
          <i class="ph ph-timer text-stone-400 text-lg"></i>
          <p class="text-sm font-semibold text-stone-700">Auto-lock</p>
        </div>
        <p class="text-xs text-stone-400 mb-3">Lock after the app is sent to the background.</p>
        <div class="flex flex-wrap gap-2">
          <button v-for="opt in autolockOptions" :key="opt.value"
            @click="setAutolock(opt.value)"
            class="px-3 py-1.5 rounded-full text-xs font-medium border transition-colors"
            :class="autolockValue === opt.value
              ? 'border-clay-400 bg-clay-50 text-clay-700'
              : 'border-stone-200 text-stone-500 hover:border-stone-300'">
            {{ opt.label }}
          </button>
        </div>
      </div>

    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()

// PIN management
const mode = ref('idle') // idle | set | change | remove
const oldPin = ref('')
const newPin = ref('')
const confirmPin = ref('')
const formError = ref('')
const busy = ref(false)

function openSet() { mode.value = 'set'; newPin.value = ''; confirmPin.value = ''; formError.value = '' }
function openChange() { mode.value = 'change'; oldPin.value = ''; newPin.value = ''; confirmPin.value = ''; formError.value = '' }
function openRemove() { mode.value = 'remove'; oldPin.value = ''; formError.value = '' }

async function doSetPin() {
  if (newPin.value.length < 4) { formError.value = 'PIN must be at least 4 characters.'; return }
  if (newPin.value !== confirmPin.value) { formError.value = 'PINs do not match.'; return }
  busy.value = true; formError.value = ''
  try {
    await ks.setLockPin(newPin.value)
    mode.value = 'idle'
  } catch { formError.value = 'Could not set PIN. Please try again.' }
  finally { busy.value = false }
}

async function doChangePin() {
  if (newPin.value.length < 4) { formError.value = 'New PIN must be at least 4 characters.'; return }
  if (newPin.value !== confirmPin.value) { formError.value = 'New PINs do not match.'; return }
  busy.value = true; formError.value = ''
  try {
    await ks.changeLockPin(oldPin.value, newPin.value)
    mode.value = 'idle'
  } catch { formError.value = 'Incorrect current PIN.' }
  finally { busy.value = false }
}

async function doRemovePin() {
  busy.value = true; formError.value = ''
  try {
    await ks.removeLockPin(oldPin.value)
    mode.value = 'idle'
  } catch { formError.value = 'Incorrect PIN.' }
  finally { busy.value = false }
}

// Auto-lock
const autolockOptions = [
  { value: '0',     label: 'Immediately' },
  { value: '1',     label: '1 min' },
  { value: '5',     label: '5 min' },
  { value: '15',    label: '15 min' },
  { value: 'never', label: 'Never' },
]

const autolockValue = ref(localStorage.getItem('ks:autolock-minutes') ?? '5')

function setAutolock(value) {
  autolockValue.value = value
  localStorage.setItem('ks:autolock-minutes', value)
}
</script>
