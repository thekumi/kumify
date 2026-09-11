<template>
  <header class="sticky top-0 z-40 bg-clay-50/90 backdrop-blur-sm">
    <div class="flex items-center h-14 px-4 gap-3">
      <button
        v-if="back"
        @click="router.back()"
        class="w-8 h-8 flex items-center justify-center -ml-1 rounded-full hover:bg-stone-100 transition-colors"
      >
        <i class="ph ph-arrow-left text-xl text-stone-600"></i>
      </button>
      <h1 class="flex-1 text-lg font-semibold text-stone-800 truncate">{{ title }}</h1>
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({
  title: { type: String, required: true },
  back: { type: Boolean, default: false },
})

const router = useRouter()
</script>
