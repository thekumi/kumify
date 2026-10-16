<template>
    <div class="pb-nav">
        <TopBar :title="id ? 'Edit Activity' : 'New Activity'" :back="true" />
        <form @submit.prevent="save" class="px-4 py-4 space-y-3">
            <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-4 space-y-4">
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Name</label>
                    <input v-model="form.name"
                           type="text"
                           required
                           placeholder="e.g. Exercise"
                           class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm" />
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Icon</label>
                    <IconPicker v-model="form.icon" fallback="ph ph-check" :color="form.color" />
                </div>
                <div v-if="categories.length">
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Category</label>
                    <select v-model="form.category"
                            class="w-full px-3 py-2.5 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-clay-400 text-stone-800 bg-stone-50 text-sm">
                        <option :value="null">No category</option>
                        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                </div>
                <div>
                    <label class="text-sm font-semibold text-stone-500 block mb-1.5">Color</label>
                    <div class="flex items-center gap-3">
                        <input v-model="form.color"
                               type="color"
                               class="w-10 h-10 rounded-xl border border-stone-200 cursor-pointer p-0.5 bg-stone-50" />
                        <span class="text-sm text-stone-500 font-mono">{{ form.color }}</span>
                    </div>
                </div>
                <div v-if="id" class="flex items-center justify-between pt-1">
                    <div>
                        <p class="text-sm font-semibold text-stone-700">Disabled</p>
                        <p class="text-xs text-stone-400 mt-0.5">Won't appear when logging moods</p>
                    </div>
                    <button type="button"
                            @click="form.hidden = !form.hidden"
                            class="relative w-10 h-5 rounded-full transition-colors shrink-0"
                            :class="form.hidden ? 'bg-stone-400' : 'bg-clay-600'">
                        <span class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
                              :class="form.hidden ? 'translate-x-5' : 'translate-x-0'"></span>
                    </button>
                </div>
            </div>
            <p v-if="error"
               class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">{{ error }}</p>
            <button type="submit"
                    :disabled="saving"
                    class="w-full py-3.5 bg-clay-600 hover:bg-clay-700 disabled:opacity-60 text-white font-semibold rounded-xl transition-colors">
                {{ saving ? 'Saving…' : (id ? 'Save changes' : 'Create activity') }}
            </button>
            <button v-if="id"
                    type="button"
                    @click="remove"
                    class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
                Delete activity
            </button>
        </form>
        <BottomNav />
    </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import IconPicker from '@/components/IconPicker.vue'
import { getActivities, createActivity, updateActivity, deleteActivity, getActivityCategories } from '@/api/mood'
import { useKeystoreStore } from '@/stores/keystore'
import { saveEncrypted } from '@/keystore/saveEncrypted'

const ks = useKeystoreStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id
const form = ref({ name: '', icon: 'ph ph-check', color: '#488460', category: null, hidden: false })
const categories = ref([])
const saving = ref(false)
const error = ref('')
let rawActivity = null

async function fillForm(activity) {
  const a = await ks.decrypt(activity)
  form.value = { name: a.name ?? '', icon: a.icon ?? 'ph ph-check', color: a.color ?? '#488460', category: activity.category ?? null, hidden: activity.hidden ?? false }
}

watch(() => ks.dataKey, async (key) => { if (key && rawActivity) await fillForm(rawActivity) })

async function save() {
  saving.value = true; error.value = ''
  try {
    if (id) {
      await saveEncrypted(updateActivity, id, form.value, ['name', 'icon', 'color'], rawActivity, ks)
    } else {
      const toEncrypt = { name: form.value.name, icon: form.value.icon || 'ph ph-check' }
      if (form.value.color) toEncrypt.color = form.value.color
      await createActivity({ category: form.value.category, encrypted_payload: await ks.encryptPayload(toEncrypt) })
    }
    router.push('/mood/settings/activities')
  } catch { error.value = 'Could not save.' }
  finally { saving.value = false }
}

async function remove() {
  if (!confirm('Delete this activity?')) return
  await deleteActivity(id)
  router.push('/mood/settings/activities')
}

onMounted(async () => {
  const [all, rawCats] = await Promise.all([getActivities({ include_hidden: 'true' }), getActivityCategories()])
  categories.value = await ks.decryptAll(rawCats)
  if (id) {
    rawActivity = all.find(a => String(a.id) === String(id))
    if (rawActivity) await fillForm(rawActivity)
  }
})
</script>
