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
    stroke-linejoin="round"
  >
    <path
      d="M14 3H6.5A1.5 1.5 0 0 0 5 4.5V19.5A1.5 1.5 0 0 0 6.5 21H17.5A1.5 1.5 0 0 0 19 19.5V8L14 3ZM14 3V8H19M9 13H15M9 17H13"
    />
  </svg>
</template>
