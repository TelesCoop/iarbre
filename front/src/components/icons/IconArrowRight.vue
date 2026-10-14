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
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
</template>
