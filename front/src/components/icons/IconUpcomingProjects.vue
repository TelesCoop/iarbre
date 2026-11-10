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
    stroke-width="1.6"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <rect x="5" y="3" width="14" height="13" rx="2" />
    <path d="M5 10h14M9 13h.01M15 13h.01" />
    <path d="M8 21l1.5-5M16 21l-1.5-5" />
  </svg>
</template>
