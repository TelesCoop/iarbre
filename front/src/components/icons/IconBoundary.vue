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
    <path d="M2 6l4-3 5 2 5-2 6 3v15l-6-3-5 2-5-2-4 3z" />
    <path d="M6 3v18" stroke-dasharray="3 2" />
    <path d="M16 3v18" stroke-dasharray="3 2" />
  </svg>
</template>
