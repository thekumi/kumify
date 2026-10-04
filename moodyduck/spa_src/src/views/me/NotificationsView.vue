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
          <button type="button" @click="toggleDaily"
            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
            :class="form.daily_reminder ? 'bg-clay-600' : 'bg-stone-200'">
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
              :class="form.daily_reminder ? 'translate-x-5' : 'translate-x-0'"></span>
          </button>
        </div>
        <div v-if="form.daily_reminder" class="flex items-center gap-3 pt-1">
          <i class="ph ph-clock text-stone-400 text-lg shrink-0"></i>
          <input v-model="form.daily_reminder_time" type="time"
            class="flex-1 text-sm text-stone-700 border-0 outline-none bg-transparent" />
        </div>
      </div>

      <!-- Habits reminder -->
      <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-stone-800">Habits reminder</p>
            <p class="text-xs text-stone-400 mt-0.5">Send together with the daily reminder</p>
          </div>
          <button type="button" @click="form.habits_reminder = !form.habits_reminder; save()"
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
          <button type="button" @click="unsubscribe"
            class="text-xs text-red-500 hover:text-red-600 font-medium shrink-0">
            Disable
          </button>
        </div>
        <div v-else class="flex items-center gap-3">
          <i class="ph ph-bell-slash text-stone-300 text-xl shrink-0"></i>
          <p class="text-sm text-stone-500 flex-1">Push not enabled on this device</p>
          <button type="button" @click="subscribe" :disabled="permissionState === 'denied' || subscribing"
            class="text-xs text-clay-600 hover:text-clay-700 font-medium shrink-0 disabled:opacity-40">
            {{ subscribing ? 'Enabling…' : 'Enable' }}
          </button>
        </div>
        <p v-if="subError" class="text-xs text-red-500">{{ subError }}</p>
      </div>

      <p v-if="saveError" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ saveError }}</p>

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
} from '@/api/notifications'

const form = ref({ daily_reminder: false, daily_reminder_time: '20:00', habits_reminder: false })
const permissionState = ref(Notification.permission)
const subscribed = ref(false)
const subscribing = ref(false)
const subError = ref('')
const saveError = ref('')
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
  if (form.value.daily_reminder && !subscribed.value) {
    await subscribe()
  }
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
    const perm = await Notification.requestPermission()
    permissionState.value = perm
    if (perm !== 'granted') {
      subError.value = 'Permission denied.'
      return
    }
    const { public_key } = await getVapidPublicKey()
    const sw = await navigator.serviceWorker.ready
    const pushSub = await sw.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(public_key),
    })
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

onMounted(async () => {
  const [settings, subs] = await Promise.all([
    getNotificationSettings().catch(() => null),
    getPushSubscriptions().catch(() => []),
  ])
  if (settings) form.value = settings

  // Check if this device already has a subscription registered
  const sw = await navigator.serviceWorker.ready.catch(() => null)
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
