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
    <path d="M6 21V6a3 3 0 0 1 3-3h2" />
    <path d="M11 3v2.5M9.5 5.5h3" />
    <path d="M4 21h4" />
    <path d="M14 13h7M14 16h7M15 16v4M20 16v4" />
  </svg>
</template>
