<script lang="ts" setup>
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"
import type { MapScorePopupData } from "@/types"

defineProps({
  popupData: {
    required: true,
    type: Object as () => MapScorePopupData
  }
})
</script>
<template>
  <div data-cy="lcz-score-popup">
    <div class="flex items-center gap-2 w-full">
      <div :style="{ backgroundColor: getZoneColor(popupData.id) }" class="w-4 h-6 rounded"></div>
      <span class="font-accent text-xl" data-cy="lcz-score-popup-title"
        >LCZ {{ popupData.id }}</span
      >
    </div>
    <div class="w-full text-md">
      {{ popupData.id }}
      <span data-cy="lcz-score-popup-description">{{ getZoneDesc(popupData.id) }}</span>
    </div>
  </div>
</template>
