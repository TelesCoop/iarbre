<script lang="ts" setup>
import { getAdaptativeColorClass } from "@/utils/color"
defineProps<{
  score: number
  total: number
  backgroundColor: string
  customSizeClass?: string
  isVertical?: boolean
}>()
</script>

<template>
  <span
    :style="{ backgroundColor: backgroundColor }"
    class="flex justify-center items-center gap-1"
    :class="[
      getAdaptativeColorClass(backgroundColor),
      customSizeClass ?? 'w-14 h-8 p-2',
      isVertical ? 'flex-col' : 'flex-row'
    ]"
  >
    <div>{{ score }}</div>
    <div
      v-if="isVertical"
      class="w-4 border-1"
      :class="getAdaptativeColorClass(backgroundColor, 'border-')"
    ></div>
    <div v-else>/</div>
    <div>{{ total }}</div>
  </span>
</template>
