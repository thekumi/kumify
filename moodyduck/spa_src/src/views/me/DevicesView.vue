<template>
  <div class="pb-nav">
    <TopBar title="Devices & Keys" :back="true" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-clay-200 border-t-clay-600 rounded-full animate-spin"></div>
    </div>

    <div v-else class="px-4 py-4 space-y-3">
      <div v-if="!devices.length" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-6 text-center">
        <i class="ph ph-devices text-5xl text-stone-300 mb-3 block"></i>
        <p class="text-stone-500 text-sm">No devices registered.</p>
      </div>

      <ul v-else class="bg-white rounded-2xl border border-stone-100 shadow-sm divide-y divide-stone-50 overflow-hidden">
        <li v-for="d in devices" :key="d.device_id" class="px-4 py-4">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                 :class="d.device_id === ks.myDeviceId ? 'bg-clay-100' : 'bg-stone-100'">
              <i class="ph ph-device-mobile text-xl"
                 :class="d.device_id === ks.myDeviceId ? 'text-clay-600' : 'text-stone-500'"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-stone-800 truncate">
                {{ d.label || 'Unnamed device' }}
                <span v-if="d.device_id === ks.myDeviceId"
                      class="ml-1.5 text-xs font-medium text-clay-600 bg-clay-100 px-1.5 py-0.5 rounded-full">This device</span>
              </p>
              <p class="text-xs text-stone-400 mt-0.5">
                Last seen: {{ d.last_seen ? fmtDate(d.last_seen) : 'never' }}
              </p>
              <p class="text-xs mt-0.5" :class="d.has_data_key ? 'text-green-600' : 'text-amber-600'">
                <i :class="d.has_data_key ? 'ph ph-check-circle' : 'ph ph-warning-circle'" class="mr-0.5"></i>
                {{ d.has_data_key ? 'Encryption key provisioned' : 'No encryption key' }}
              </p>
            </div>
          </div>

          <div v-if="!d.has_data_key && ks.dataKey" class="mt-3 flex gap-2">
            <button @click="grantKey(d)" :disabled="granting === d.device_id"
              class="flex-1 py-2 text-xs font-medium rounded-xl bg-green-50 text-green-700 hover:bg-green-100 disabled:opacity-60 transition-colors border border-green-200">
              {{ granting === d.device_id ? 'Granting…' : 'Grant encryption access' }}
            </button>
          </div>

          <div v-if="d.device_id !== ks.myDeviceId" class="mt-2">
            <button @click="remove(d)" :disabled="removing === d.device_id"
              class="text-xs text-red-500 hover:text-red-700 disabled:opacity-60 transition-colors">
              {{ removing === d.device_id ? 'Removing…' : 'Remove device' }}
            </button>
          </div>
        </li>
      </ul>

      <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getDevices, deleteDevice } from '@/api/profile'
import { useKeystoreStore } from '@/stores/keystore'

const ks = useKeystoreStore()
const devices = ref([])
const loading = ref(true)
const granting = ref(null)
const removing = ref(null)
const error = ref('')

const fmtDate = (ts) => new Date(ts).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })

async function grantKey(device) {
  granting.value = device.device_id
  error.value = ''
  try {
    await ks.grantKey(device)
    device.has_data_key = true
  } catch {
    error.value = 'Could not grant key. Try again.'
  } finally {
    granting.value = null
  }
}

async function remove(device) {
  if (!confirm(`Remove "${device.label || 'this device'}"? It will lose access to your encrypted data.`)) return
  removing.value = device.device_id
  error.value = ''
  try {
    await deleteDevice(device.device_id)
    devices.value = devices.value.filter(d => d.device_id !== device.device_id)
  } catch {
    error.value = 'Could not remove device. Try again.'
  } finally {
    removing.value = null
  }
}

async function fetchDevices() {
  devices.value = await getDevices()
  loading.value = false
}

// Reload whenever the keystore finishes registering this device —
// the list fetch can race ahead of boot() completing.
watch(() => ks.myDeviceId, (id) => { if (id) fetchDevices() })

onMounted(fetchDevices)
</script>
