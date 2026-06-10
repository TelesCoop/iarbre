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
    <path d="M2 21h20" />
    <rect x="3.5" y="10" width="6" height="11" />
    <rect x="12.5" y="4" width="8" height="17" />
    <path d="M15.5 21v-3.5h2V21" />
    <path d="M5.5 13.5h.01M5.5 16.5h.01" />
  </svg>
</template>
