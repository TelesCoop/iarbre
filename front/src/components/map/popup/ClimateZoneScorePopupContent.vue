<script lang="ts" setup>
import { getZoneDesc, getZoneColor } from "@/utils/climateZone"
import type { MapScorePopupData } from "@/types/map"

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
      <div
        :style="{ backgroundColor: getZoneColor(popupData.score) }"
        class="w-4 h-6 rounded"
      ></div>
      <span class="font-accent text-xl" data-cy="lcz-score-popup-title"
        >LCZ {{ popupData.score }}</span
      >
    </div>
    <div class="w-full text-md mb-2">
      {{ popupData.score }}
      <span data-cy="lcz-score-popup-description">{{ getZoneDesc(popupData.score) }}</span>
    </div>
    <div class="flex w-full items-center justify-center">
      <show-hide-score-button :feature-id="popupData.id" data-cy="toggle-climate-zone-details" />
    </div>
  </div>
</template>
