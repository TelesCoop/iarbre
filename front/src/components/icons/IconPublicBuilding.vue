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
    <path d="M3 9.5 12 4l9 5.5" />
    <path d="M4 9.5h16" />
    <path d="M6 12v6M10 12v6M14 12v6M18 12v6" />
    <path d="M4 18h16" />
  </svg>
</template>
