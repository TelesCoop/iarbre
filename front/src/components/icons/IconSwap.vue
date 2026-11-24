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
    <path d="M4 8h15" />
    <path d="M15 4l4 4-4 4" />
    <path d="M20 16H5" />
    <path d="M9 12l-4 4 4 4" />
  </svg>
</template>
