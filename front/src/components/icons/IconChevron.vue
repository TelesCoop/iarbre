<script lang="ts" setup>
interface Props {
  size?: number
  direction?: "up" | "down" | "left" | "right"
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
  direction: "down"
})

const rotation = {
  up: "rotate-180",
  down: "rotate-0",
  left: "rotate-90",
  right: "-rotate-90"
}
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
    :class="['transition-transform', rotation[props.direction]]"
  >
    <path d="m6 9 6 6 6-6" />
  </svg>
</template>
