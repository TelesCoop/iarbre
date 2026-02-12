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
    <path d="M12 2v20" />
    <path d="M4 7h16" />
    <path d="M4 7l3 7H1L4 7z" />
    <path d="M20 7l3 7h-6L20 7z" />
    <path d="M9 22h6" />
  </svg>
</template>
