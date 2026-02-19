<script lang="ts" setup>
import { VegetationLegend } from "@/utils/vegetation"
</script>

<template>
  <div
    class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1"
    data-cy="vegetation-legend"
  >
    <div
      v-for="(color, name, index) in VegetationLegend"
      :key="index"
      class="flex items-center gap-2"
    >
      <div
        :style="{ backgroundColor: color }"
        class="w-4 h-4 border border-gray-300 rounded-sm"
      ></div>
      <span class="text-sm text-primary-900">{{ name }}</span>
    </div>
  </div>
</template>
