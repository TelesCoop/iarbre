<script lang="ts" setup>
interface Props {
  size?: number
}

withDefaults(defineProps<Props>(), {
  size: 44
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.4"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path
      d="M12 2.5c-3.4 0-6.1 2.6-6.1 5.9 0 2.9 2.1 5.3 4.9 5.8v6.4h2.4v-6.4c2.8-.5 4.9-2.9 4.9-5.8 0-3.3-2.7-5.9-6.1-5.9Z"
    />
  </svg>
</template>
