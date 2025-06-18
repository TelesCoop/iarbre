<script lang="ts" setup>
import { getAdaptativeColorClass } from "@/utils/color"
defineProps<{
  score: number
  total: number
  backgroundColor: string
  customSizeClass?: string
}>()
</script>

<template>
  <span
    :style="{ backgroundColor: backgroundColor }"
    class="rounded flex justify-center items-center"
    :class="[getAdaptativeColorClass(backgroundColor), customSizeClass ?? 'w-14 h-8 p-2']"
  >
    {{ score }} / {{ total }}
  </span>
</template>
