<template>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <!-- neck first — body fill covers the part that goes under -->
    <path d="M19 16.5 Q16 19 14 21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    <ellipse cx="13" cy="21" rx="9" ry="6" :fill="bg" stroke="currentColor" stroke-width="1.5"/>
    <circle cx="22" cy="12" r="5" :fill="bg" stroke="currentColor" stroke-width="1.5"/>
    <path d="M7 21.5 Q13 18.5 19 21.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M27 11.5 L31 12 L27 13.5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="23.5" cy="11" r="1" fill="currentColor"/>
  </svg>
</template>

<script setup>
defineProps({
  bg: { type: String, required: true },
})
</script>
