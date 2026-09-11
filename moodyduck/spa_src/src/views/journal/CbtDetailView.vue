<template>
  <div class="pb-nav">
    <TopBar :title="record?.title || 'Thought Record'" :back="true">
      <template #actions>
        <RouterLink :to="`/journal/cbt/${id}/edit`" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 transition-colors">
          <i class="ph ph-pencil-simple text-stone-600"></i>
        </RouterLink>
      </template>
    </TopBar>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="record" class="px-4 py-4 space-y-3">
      <div v-if="record.encrypted_payload" class="bg-amber-50 rounded-2xl border border-amber-100 p-4 flex items-center gap-3">
        <i class="ph ph-lock text-amber-600 text-xl shrink-0"></i>
        <p class="text-sm text-amber-800">This record is encrypted.</p>
      </div>

      <template v-if="!record.encrypted_payload">
        <div v-if="record.situation" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
          <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-2">Situation</p>
          <p class="text-stone-700 text-sm leading-relaxed whitespace-pre-wrap">{{ record.situation }}</p>
        </div>
        <div v-if="record.thoughts" class="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
          <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider mb-2">Thoughts</p>
          <p class="text-stone-700 text-sm leading-relaxed whitespace-pre-wrap">{{ record.thoughts }}</p>
        </div>
      </template>

      <button @click="remove" class="w-full py-3 rounded-xl border border-red-100 bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition-colors">
        Delete record
      </button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import { getRecord, deleteRecord } from '@/api/cbt'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const record = ref(null)
const loading = ref(true)

async function remove() {
  if (!confirm('Delete this record?')) return
  await deleteRecord(id)
  router.push('/journal/cbt')
}

onMounted(async () => { record.value = await getRecord(id); loading.value = false })
</script>
