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
    <rect x="2" y="11" width="20" height="11" />
    <path d="M6 11V7" />
    <path d="M18 11V7" />
    <path d="M6 7h12" />
    <path d="M12 2l8 5H4l8-5z" />
    <rect x="9" y="15" width="6" height="7" />
  </svg>
</template>
