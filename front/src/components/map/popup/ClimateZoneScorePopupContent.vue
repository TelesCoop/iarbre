<script setup lang="ts">
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
      <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(popupData.id) }"></div>
      <span class="text-[0.9rem]" data-cy="lcz-score-popup-title">LCZ {{ popupData.id }}</span>
    </div>
    <div class="w-full">
      {{ popupData.id }}
      <span class="text-[0.9rem]" data-cy="lcz-score-popup-description">{{
        getZoneDesc(popupData.id)
      }}</span>
    </div>
  </div>
</template>
