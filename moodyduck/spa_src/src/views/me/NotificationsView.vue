<template>
    <div class="pb-nav">
        <TopBar title="Notifications" :back="true" />
        <div class="px-4 py-4 space-y-4">
            <!-- Permission banner -->
            <div v-if="permissionState === 'denied'"
                 class="bg-red-50 border border-red-100 rounded-2xl px-4 py-3 text-sm text-red-700">
                Notifications are blocked in your browser. Enable them in browser settings to use this feature.
            </div>
            <!-- Daily reminder -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-semibold text-stone-800">Daily reminder</p>
                        <p class="text-xs text-stone-400 mt-0.5">Get a nudge to log your mood each day</p>
                    </div>
                    <button type="button"
                            @click="toggleDaily"
                            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
                            :class="form.daily_reminder ? 'bg-clay-600' : 'bg-stone-200'">
                        <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                              :class="form.daily_reminder ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                </div>
                <div v-if="form.daily_reminder && needsAlarmPermission"
                     class="flex items-start gap-3 bg-amber-50 border border-amber-100 rounded-xl px-3 py-2.5">
                    <i class="ph ph-warning text-amber-500 text-lg shrink-0 mt-0.5"></i>
                    <div class="flex-1 min-w-0">
                        <p class="text-xs text-amber-800 font-medium">Exact alarm permission needed</p>
                        <p class="text-xs text-amber-700 mt-0.5">Without it, reminders may fire late. Grant it in Settings to get notified at the exact time you set.</p>
                    </div>
                    <button type="button"
                            @click="requestAlarmPermission"
                            class="text-xs font-semibold text-amber-700 hover:text-amber-900 shrink-0 mt-0.5 transition-colors">
                        Grant
                    </button>
                </div>
                <div v-if="form.daily_reminder" class="space-y-2 pt-1">
                    <div v-for="(t, i) in form.daily_reminder_times"
                         :key="i"
                         class="flex items-center gap-2">
                        <i class="ph ph-clock text-stone-400 text-lg shrink-0"></i>
                        <input :value="t"
                               @change="updateTime(i, $event.target.value)"
                               type="time"
                               class="flex-1 text-sm text-stone-700 border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-clay-400" />
                        <button type="button"
                                @click="removeTime(i)"
                                :disabled="form.daily_reminder_times.length <= 1"
                                class="w-7 h-7 flex items-center justify-center rounded-full hover:bg-red-50 text-stone-300 hover:text-red-400 transition-colors disabled:opacity-30 shrink-0">
                            <i class="ph ph-minus-circle text-lg"></i>
                        </button>
                    </div>
                    <button type="button"
                            @click="addTime"
                            class="flex items-center gap-1.5 text-sm text-clay-600 hover:text-clay-700 font-medium transition-colors pl-7">
                        <i class="ph ph-plus-circle"></i> Add time
                    </button>
                </div>
            </div>
            <!-- Habits reminder -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-semibold text-stone-800">Habits reminder</p>
                        <p class="text-xs text-stone-400 mt-0.5">Send together with the daily reminder</p>
                    </div>
                    <button type="button"
                            @click="form.habits_reminder = !form.habits_reminder; save()"
                            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
                            :class="form.habits_reminder ? 'bg-clay-600' : 'bg-stone-200'">
                        <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                              :class="form.habits_reminder ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                </div>
            </div>
            <!-- Subscription status -->
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">This device</p>
                <div v-if="subscribed" class="flex items-center gap-3">
                    <i class="ph ph-check-circle text-green-500 text-xl shrink-0"></i>
                    <p class="text-sm text-stone-700 flex-1">Push enabled on this device</p>
                    <button type="button"
                            @click="unsubscribe"
                            class="text-xs text-red-500 hover:text-red-600 font-medium shrink-0">Disable</button>
                </div>
                <div v-else class="flex items-center gap-3">
                    <i class="ph ph-bell-slash text-stone-300 text-xl shrink-0"></i>
                    <p class="text-sm text-stone-500 flex-1">Push not enabled on this device</p>
                    <button type="button"
                            @click="subscribe"
                            :disabled="permissionState === 'denied' || subscribing"
                            class="text-xs text-clay-600 hover:text-clay-700 font-medium shrink-0 disabled:opacity-40">
                        {{ subscribing ? 'Enabling…' : 'Enable' }}
                    </button>
                </div>
                <p v-if="subError" class="text-xs text-red-500">{{ subError }}</p>
            </div>
            <!-- Test notification -->
            <div v-if="subscribed || isAndroid"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-3">
                <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider">Test</p>
                <div class="flex items-center gap-3">
                    <i v-if="testSent"
                       class="ph ph-check-circle text-green-500 text-xl shrink-0"></i>
                    <i v-else class="ph ph-paper-plane-tilt text-stone-300 text-xl shrink-0"></i>
                    <p class="text-sm text-stone-700 flex-1">
                        <template v-if="testSent">Notification sent — check your device</template>
                        <template v-else>Send a test notification to this device</template>
                    </p>
                    <button type="button"
                            @click="sendTest"
                            :disabled="testing || testSent"
                            class="text-xs text-clay-600 hover:text-clay-700 font-medium shrink-0 disabled:opacity-40">
                        {{ testing ? 'Sending…' : testSent ? 'Sent' : 'Send' }}
                    </button>
                </div>
                <p v-if="testError" class="text-xs text-red-500">{{ testError }}</p>
            </div>
            <!-- Contacts sync (Android only) -->
            <div v-if="isAndroid"
                 class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-semibold text-stone-800">Sync contacts</p>
                        <p class="text-xs text-stone-400 mt-0.5">Keep your People list in the Android Contacts app</p>
                    </div>
                    <button type="button"
                            @click="toggleContacts"
                            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
                            :class="contactsEnabled ? 'bg-clay-600' : 'bg-stone-200'">
                        <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                              :class="contactsEnabled ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                </div>
            </div>
            <p v-if="saveError"
               class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ saveError }}</p>
        </div>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import {
  getVapidPublicKey,
  getNotificationSettings,
  updateNotificationSettings,
  registerPushSubscription,
  deletePushSubscription,
  getPushSubscriptions,
  sendTestNotification,
} from '@/api/notifications'
import { useKeystoreStore } from '@/stores/keystore'
import { syncAndroidContacts, CONTACTS_ENABLED_KEY } from '@/androidContacts'

const ks = useKeystoreStore()
const isAndroid = !!window.Android

const form = ref({ daily_reminder: false, daily_reminder_times: ['20:00'], habits_reminder: false })
const contactsEnabled = ref(localStorage.getItem(CONTACTS_ENABLED_KEY) === '1')
const permissionState = ref(typeof Notification !== 'undefined' ? Notification.permission : 'default')
const needsAlarmPermission = ref(false)
const subscribed = ref(false)
const subscribing = ref(false)
const subError = ref('')
const saveError = ref('')
const testing = ref(false)
const testSent = ref(false)
const testError = ref('')
let existingSubId = null
let saveTimer = null

// Debounced auto-save when form changes
watch(form, () => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(save, 800)
}, { deep: true })

async function save() {
  try {
    await updateNotificationSettings(form.value)
    saveError.value = ''
  } catch {
    saveError.value = 'Could not save settings.'
  }
}

async function toggleDaily() {
  form.value.daily_reminder = !form.value.daily_reminder
  if (form.value.daily_reminder && !subscribed.value && !isAndroid) {
    await subscribe()
  }
  syncAndroidCheckIns()
}

function addTime() {
  form.value.daily_reminder_times = [...form.value.daily_reminder_times, '20:00']
  syncAndroidCheckIns()
}

function removeTime(i) {
  if (form.value.daily_reminder_times.length <= 1) return
  form.value.daily_reminder_times = form.value.daily_reminder_times.filter((_, idx) => idx !== i)
  syncAndroidCheckIns()
}

function updateTime(i, value) {
  const times = [...form.value.daily_reminder_times]
  times[i] = value
  form.value.daily_reminder_times = times
  syncAndroidCheckIns()
}

function syncAndroidCheckIns() {
  if (!window.Android?.scheduleDailyCheckIns) return
  if (!form.value.daily_reminder) {
    window.Android.cancelDailyCheckIns?.()
    needsAlarmPermission.value = false
    return
  }
  const canExact = window.Android.canScheduleExactAlarms?.() ?? true
  needsAlarmPermission.value = !canExact
  const payload = form.value.daily_reminder_times.map(t => {
    const [h, m] = t.split(':').map(Number)
    return { hour: h, minute: m }
  })
  window.Android.scheduleDailyCheckIns(JSON.stringify(payload))
}

function requestAlarmPermission() {
  window.Android.requestExactAlarmPermission?.()
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  return Uint8Array.from(raw, c => c.charCodeAt(0))
}

async function subscribe() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    subError.value = 'Push notifications are not supported in this browser.'
    return
  }
  subscribing.value = true
  subError.value = ''
  try {
    const perm = typeof Notification !== 'undefined' ? await Notification.requestPermission() : 'denied'
    permissionState.value = perm
    if (perm !== 'granted') {
      subError.value = 'Permission denied.'
      return
    }
    const { public_key } = await getVapidPublicKey()
    if (!public_key) {
      subError.value = 'Push notifications are not configured on this server.'
      return
    }
    let reg = await navigator.serviceWorker.getRegistration()
    if (!reg) {
      try {
        reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' })
      } catch (err) {
        subError.value = `Service worker registration failed: ${err.message}`
        return
      }
    }
    const sw = await Promise.race([
      navigator.serviceWorker.ready,
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Service worker is not active — try reloading the page.')), 15000)
      ),
    ])
    const pushSub = await Promise.race([
      sw.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      }),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Push service not responding — check your connection and try again.')), 30000)
      ),
    ])
    const json = pushSub.toJSON()
    const saved = await registerPushSubscription({
      endpoint: json.endpoint,
      p256dh: json.keys.p256dh,
      auth: json.keys.auth,
    })
    existingSubId = saved.id
    subscribed.value = true
  } catch (e) {
    subError.value = e.message || 'Could not enable push notifications.'
  } finally {
    subscribing.value = false
  }
}

async function unsubscribe() {
  try {
    const sw = await navigator.serviceWorker.ready
    const pushSub = await sw.pushManager.getSubscription()
    if (pushSub) await pushSub.unsubscribe()
    if (existingSubId) await deletePushSubscription(existingSubId)
    subscribed.value = false
    existingSubId = null
  } catch {
    subError.value = 'Could not disable push notifications.'
  }
}

async function sendTest() {
  testing.value = true
  testError.value = ''
  try {
    await sendTestNotification()
    testSent.value = true
    setTimeout(() => { testSent.value = false }, 5000)
  } catch {
    testError.value = 'Could not send test notification.'
  } finally {
    testing.value = false
  }
}

async function toggleContacts() {
  if (contactsEnabled.value) {
    contactsEnabled.value = false
    localStorage.removeItem(CONTACTS_ENABLED_KEY)
    window.Android?.removeContacts?.()
  } else {
    contactsEnabled.value = true
    localStorage.setItem(CONTACTS_ENABLED_KEY, '1')
    await syncAndroidContacts(ks).catch(() => {})
  }
}

onMounted(async () => {
  const [settings, subs] = await Promise.all([
    getNotificationSettings().catch(() => null),
    getPushSubscriptions().catch(() => []),
  ])
  if (settings) {
    form.value = {
      ...settings,
      daily_reminder_times: settings.daily_reminder_times?.length ? settings.daily_reminder_times : ['20:00'],
    }
  }
  syncAndroidCheckIns()

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') syncAndroidCheckIns()
  })

  // Check if this device already has a subscription registered
  const reg = await navigator.serviceWorker.getRegistration().catch(() => null)
  const sw = reg ? await Promise.race([
    navigator.serviceWorker.ready,
    new Promise(resolve => setTimeout(resolve, 5000, null)),
  ]) : null
  if (sw) {
    const pushSub = await sw.pushManager.getSubscription().catch(() => null)
    if (pushSub) {
      const match = subs.find(s => s.endpoint === pushSub.endpoint)
      if (match) {
        subscribed.value = true
        existingSubId = match.id
      }
    }
  }
})
</script>
