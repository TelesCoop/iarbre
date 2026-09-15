<script lang="ts" setup>
interface Props {
  size?: number
}

withDefaults(defineProps<Props>(), {
  size: 16
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <path d="M4 8 9 4 15 6 20 10 17 18 8 17 Z" />
    <circle cx="12" cy="11" r="1.5" fill="currentColor" stroke="none" />
  </svg>
</template>
