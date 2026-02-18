<script lang="ts" setup>
import { BiosphereIntegrityLegend } from "@/utils/biosphere_functional_integrity"
</script>

<template>
  <div class="font-accent text-xs leading-3 overflow-visible" data-cy="biosphere-integrity-legend">
    <div
      v-for="(color, name, index) in BiosphereIntegrityLegend"
      :key="index"
      class="flex items-center gap-2"
    >
      <div
        class="w-4 h-4 border border-gray-300 rounded-sm"
        :style="{ backgroundColor: color }"
      ></div>
      <span class="text-sm text-primary-900">{{ name }}</span>
    </div>
  </div>
</template>
