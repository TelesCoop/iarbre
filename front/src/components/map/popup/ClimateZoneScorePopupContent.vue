<script setup lang="ts">
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"

defineProps({
  index: {
    required: true,
    type: String
  }
})
</script>
<template>
  <div data-cy="lcz-score-popup">
    <div class="flex items-center gap-2 w-full">
      <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(index) }"></div>
      <span class="text-[0.9rem]" data-cy="lcz-score-popup-title">LCZ {{ index }}</span>
    </div>
    <div class="w-full">
      <span class="text-[0.9rem]" data-cy="lcz-score-popup-description">{{
        getZoneDesc(index)
      }}</span>
    </div>
  </div>
</template>
