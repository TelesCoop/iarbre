<template>
  <div data-cy="lcz-score-popup">
    <div class="flex items-center gap-2 w-full">
      <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(index) }"></div>
      <span class="text-[0.9rem]">LCZ {{ index }}</span>
    </div>
    <div class="w-full">
      <span class="text-[0.9rem]">{{ getZoneDesc(index) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"

const props = defineProps({
  index: {
    required: true,
    type: String
  }
})
</script>
