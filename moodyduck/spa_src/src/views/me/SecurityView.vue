<template>
    <div class="pb-nav">
        <TopBar title="Privacy & Security" :back="true" />
        <div class="px-4 py-4 space-y-4">
            <!-- Account password -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <div class="flex items-center gap-2 mb-1">
                    <i class="ph ph-key text-stone-400 text-lg"></i>
                    <p class="text-sm font-semibold text-stone-700">Account password</p>
                </div>
                <p class="text-xs text-stone-400 leading-relaxed">Change the password you use to sign in to MoodyDuck.</p>
                <template v-if="pwMode === 'change'">
                    <input v-model="pwCurrent"
                           type="password"
                           placeholder="Current password"
                           autocomplete="current-password"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-model="pwNew"
                           type="password"
                           placeholder="New password"
                           autocomplete="new-password"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-model="pwConfirm"
                           type="password"
                           placeholder="Confirm new password"
                           autocomplete="new-password"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <p v-if="pwError"
                       class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ pwError }}</p>
                    <p v-if="pwSuccess"
                       class="text-xs text-green-700 bg-green-50 rounded-xl px-3 py-2">{{ pwSuccess }}</p>
                    <div class="flex gap-2">
                        <button type="button"
                                @click="pwMode = 'idle'; pwCurrent = ''; pwNew = ''; pwConfirm = ''; pwError = ''; pwSuccess = ''"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
                        <button type="button"
                                @click="doChangePassword"
                                :disabled="pwBusy"
                                class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
                            {{ pwBusy ? 'Saving…' : 'Change password' }}
                        </button>
                    </div>
                </template>
                <template v-else>
                    <p v-if="pwSuccess"
                       class="text-xs text-green-700 bg-green-50 rounded-xl px-3 py-2">{{ pwSuccess }}</p>
                    <button type="button"
                            @click="pwMode = 'change'; pwError = ''"
                            class="w-full py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">
                        Change password
                    </button>
                </template>
            </div>
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
                    <input v-model="newPin"
                           type="password"
                           placeholder="New PIN or passphrase (min 4 chars)"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-model="confirmPin"
                           type="password"
                           placeholder="Confirm PIN"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <p v-if="formError"
                       class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
                    <div class="flex gap-2">
                        <button type="button"
                                @click="mode = 'idle'"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
                        <button type="button"
                                @click="doSetPin"
                                :disabled="busy"
                                class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
                            {{ busy ? 'Saving…' : 'Set PIN' }}
                        </button>
                    </div>
                </template>
                <!-- Change PIN form -->
                <template v-else-if="mode === 'change'">
                    <input v-model="oldPin"
                           type="password"
                           placeholder="Current PIN"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-model="newPin"
                           type="password"
                           placeholder="New PIN (min 4 chars)"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <input v-model="confirmPin"
                           type="password"
                           placeholder="Confirm new PIN"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                    <p v-if="formError"
                       class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
                    <div class="flex gap-2">
                        <button type="button"
                                @click="mode = 'idle'"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
                        <button type="button"
                                @click="doChangePin"
                                :disabled="busy"
                                class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
                            {{ busy ? 'Saving…' : 'Change PIN' }}
                        </button>
                    </div>
                </template>
                <!-- Remove PIN form -->
                <template v-else-if="mode === 'remove'">
                    <p class="text-xs text-amber-700 bg-amber-50 rounded-xl px-3 py-2">
                        This will store your encryption key unprotected in the browser. Anyone with access to this device could potentially read it.
                    </p>
                    <input v-model="oldPin"
                           type="password"
                           placeholder="Current PIN to confirm"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-red-400 text-stone-800 bg-stone-50 text-sm" />
                    <p v-if="formError"
                       class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ formError }}</p>
                    <div class="flex gap-2">
                        <button type="button"
                                @click="mode = 'idle'"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
                        <button type="button"
                                @click="doRemovePin"
                                :disabled="busy || !oldPin"
                                class="flex-1 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
                            {{ busy ? 'Removing…' : 'Remove PIN' }}
                        </button>
                    </div>
                </template>
                <!-- Idle state buttons -->
                <template v-else>
                    <button type="button"
                            v-if="!ks.lockConfigured"
                            @click="openSet"
                            class="w-full py-2.5 bg-clay-600 hover:bg-clay-700 text-white text-sm font-semibold rounded-xl transition-colors">
                        Set Lock PIN
                    </button>
                    <div v-else class="flex gap-2">
                        <button type="button"
                                @click="openChange"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Change PIN</button>
                        <button type="button"
                                @click="openRemove"
                                class="flex-1 py-2.5 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">Remove PIN</button>
                    </div>
                </template>
            </div>
            <!-- Biometric unlock (Android only) -->
            <div v-if="androidBiometricAvailable"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <div class="flex items-center gap-2 mb-1">
                    <i class="ph ph-fingerprint text-stone-400 text-lg"></i>
                    <p class="text-sm font-semibold text-stone-700">Biometric unlock</p>
                    <span class="ml-auto text-xs font-medium px-2 py-0.5 rounded-full"
                          :class="androidBiometricPinStored ? 'bg-green-100 text-green-700' : 'bg-stone-100 text-stone-500'">
                        {{ androidBiometricPinStored ? 'Active' : 'Not set up' }}
                    </span>
                </div>
                <p class="text-xs text-stone-400 leading-relaxed">
                    Use your fingerprint or face to unlock instead of typing your PIN.
                    Your PIN is encrypted in the Android Keystore and never leaves this device.
                </p>
                <p v-if="biometricError"
                   class="text-xs text-red-600 bg-red-50 rounded-xl px-3 py-2">{{ biometricError }}</p>
                <!-- Not yet set up -->
                <template v-if="!androidBiometricPinStored">
                    <p v-if="!ks.lockConfigured"
                       class="text-xs text-stone-400">Set a lock PIN first to enable biometric unlock.</p>
                    <template v-else-if="!showBiometricSetup">
                        <button type="button"
                                @click="showBiometricSetup = true; biometricError = ''"
                                class="w-full py-2.5 bg-clay-600 hover:bg-clay-700 text-white text-sm font-semibold rounded-xl transition-colors">
                            Set up biometric unlock
                        </button>
                    </template>
                    <template v-else>
                        <input v-model="biometricSetupPin"
                               type="password"
                               placeholder="Enter current PIN to confirm"
                               class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                        <div class="flex gap-2">
                            <button type="button"
                                    @click="showBiometricSetup = false; biometricSetupPin = ''; biometricError = ''"
                                    class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition-colors">Cancel</button>
                            <button type="button"
                                    @click="doSetupBiometric"
                                    :disabled="biometricBusy || !biometricSetupPin"
                                    class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl transition-colors">
                                {{ biometricBusy ? 'Setting up…' : 'Enable' }}
                            </button>
                        </div>
                    </template>
                </template>
                <!-- Already active -->
                <button v-else
                        type="button"
                        @click="doRemoveBiometric"
                        class="w-full py-2.5 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                    Remove biometric unlock
                </button>
            </div>
            <!-- Auto-lock -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                <div class="flex items-center gap-2 mb-1">
                    <i class="ph ph-timer text-stone-400 text-lg"></i>
                    <p class="text-sm font-semibold text-stone-700">Auto-lock</p>
                </div>
                <p class="text-xs text-stone-400 mb-3">Lock after the app is sent to the background.</p>
                <div class="flex flex-wrap gap-2">
                    <button type="button"
                            v-for="opt in autolockOptions"
                            :key="opt.value"
                            @click="setAutolock(opt.value)"
                            class="px-3 py-1.5 rounded-full text-xs font-medium border transition-colors"
                            :class="autolockValue === opt.value
              ? 'border-clay-400 bg-clay-50 text-clay-700'
              : 'border-stone-200 text-stone-500 hover:border-stone-300'">{{ opt.label }}</button>
                </div>
            </div>
            <!-- Encryption health check -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <div class="flex items-center gap-2 mb-1">
                    <i class="ph ph-shield-check text-stone-400 text-lg"></i>
                    <p class="text-sm font-semibold text-stone-700">Encryption health</p>
                </div>
                <p class="text-xs text-stone-400 leading-relaxed">
                    Scans all your data for records that are encrypted but still retain readable plaintext
                    fields, then wipes those leftover values.
                </p>
                <div v-if="scrubResult"
                     class="text-xs rounded-xl px-3 py-2"
                     :class="scrubResult.ok ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'">
                    {{ scrubResult.message }}
                </div>
                <div v-if="scrubCounts && !scrubBusy" class="space-y-1">
                    <p class="text-xs font-medium text-stone-500">Records with residual plaintext:</p>
                    <ul class="text-xs text-stone-500 space-y-0.5">
                        <li v-for="(count, key) in scrubCounts"
                            :key="key"
                            v-show="count > 0"
                            class="flex justify-between">
                            <span>{{ key.replace(/_/g, ' ') }}</span>
                            <span class="font-semibold text-amber-600">{{ count }}</span>
                        </li>
                        <li v-if="!Object.values(scrubCounts).some(c => c > 0)"
                            class="text-green-600 font-medium">All clean — no residual plaintext found.</li>
                    </ul>
                </div>
                <div class="flex gap-2">
                    <button type="button"
                            @click="doCheckScrub"
                            :disabled="scrubBusy || !ks.dataKey"
                            class="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 disabled:opacity-50 transition-colors">
                        {{ scrubBusy ? 'Checking…' : 'Check' }}
                    </button>
                    <button type="button"
                            @click="doRunScrub"
                            :disabled="scrubBusy || !ks.dataKey"
                            class="flex-1 py-2.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors">
                        {{ scrubBusy ? 'Running…' : 'Fix & clean' }}
                    </button>
                </div>
            </div>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { useKeystoreStore } from '@/stores/keystore'
import { useAuthStore } from '@/stores/auth'
import { changePassword } from '@/api/auth'
import { checkScrub, runScrub } from '@/keystore/scrub.js'

const ks = useKeystoreStore()
const auth = useAuthStore()

// Account password change
const pwMode = ref('idle')
const pwCurrent = ref('')
const pwNew = ref('')
const pwConfirm = ref('')
const pwError = ref('')
const pwSuccess = ref('')
const pwBusy = ref(false)

async function doChangePassword() {
  if (pwNew.value !== pwConfirm.value) { pwError.value = 'New passwords do not match.'; return }
  pwBusy.value = true; pwError.value = ''
  try {
    const { token } = await changePassword(pwCurrent.value, pwNew.value)
    localStorage.setItem('authToken', token)
    pwMode.value = 'idle'
    pwCurrent.value = ''; pwNew.value = ''; pwConfirm.value = ''
    pwSuccess.value = 'Password changed successfully.'
  } catch (e) {
    const data = e.data ?? {}
    pwError.value = data.current_password?.[0] ?? data.new_password?.[0] ?? 'Could not change password.'
  } finally {
    pwBusy.value = false
  }
}

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
    await mirrorPinToBiometric(newPin.value)
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
    await mirrorPinToBiometric(newPin.value)
  } catch { formError.value = 'Incorrect current PIN.' }
  finally { busy.value = false }
}

async function doRemovePin() {
  busy.value = true; formError.value = ''
  try {
    await ks.removeLockPin(oldPin.value)
    mode.value = 'idle'
    window.Android?.clearBiometricPin?.()
    androidBiometricPinStored.value = false
  } catch { formError.value = 'Incorrect PIN.' }
  finally { busy.value = false }
}

// Biometric (Android bridge)
const androidBiometricAvailable = computed(() => !!window.Android?.isBiometricAvailable?.())
const androidBiometricPinStored = ref(window.Android?.hasBiometricPin?.() ?? false)
const biometricBusy = ref(false)
const biometricError = ref('')
const showBiometricSetup = ref(false)
const biometricSetupPin = ref('')

async function mirrorPinToBiometric(pin) {
  if (!androidBiometricAvailable.value) return
  try {
    await window.Android.savePinBiometricAsync(pin)
    androidBiometricPinStored.value = true
  } catch { /* user dismissed biometric prompt — non-fatal */ }
}

async function doSetupBiometric() {
  if (biometricSetupPin.value.length < 4) { biometricError.value = 'Enter your current PIN.'; return }
  biometricBusy.value = true; biometricError.value = ''
  try {
    // Verify the PIN is correct by re-wrapping with the same value (throws on wrong PIN)
    await ks.changeLockPin(biometricSetupPin.value, biometricSetupPin.value)
    await window.Android.savePinBiometricAsync(biometricSetupPin.value)
    androidBiometricPinStored.value = true
    biometricSetupPin.value = ''
    showBiometricSetup.value = false
  } catch { biometricError.value = 'Incorrect PIN.' }
  finally { biometricBusy.value = false }
}

function doRemoveBiometric() {
  window.Android?.clearBiometricPin?.()
  androidBiometricPinStored.value = false
}

// Encryption scrub
const scrubBusy = ref(false)
const scrubCounts = ref(null)
const scrubResult = ref(null)

async function doCheckScrub() {
  scrubBusy.value = true
  scrubResult.value = null
  try {
    scrubCounts.value = await checkScrub()
  } finally {
    scrubBusy.value = false
  }
}

async function doRunScrub() {
  scrubBusy.value = true
  scrubResult.value = null
  scrubCounts.value = null
  try {
    const { staged, scrubbed } = await runScrub(ks.dataKey)
    const total = staged + scrubbed
    scrubResult.value = {
      ok: true,
      message: total === 0
        ? 'Nothing to clean — all records are already tidy.'
        : `Done. Encrypted ${staged} record${staged !== 1 ? 's' : ''}, wiped plaintext from ${scrubbed} record${scrubbed !== 1 ? 's' : ''}.`,
    }
    scrubCounts.value = await checkScrub()
  } catch {
    scrubResult.value = { ok: false, message: 'Scrub failed. Please try again.' }
  } finally {
    scrubBusy.value = false
  }
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
