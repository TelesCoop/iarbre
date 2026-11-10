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
    <path d="M2 7h20" />
    <rect x="5" y="10" width="14" height="11" rx="2" stroke-dasharray="2.5 2.5" />
    <path d="M10.5 18.5v-6h2.25a1.75 1.75 0 0 1 0 3.5H10.5" />
  </svg>
</template>
