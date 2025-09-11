<script lang="ts" setup>
import { getZoneDesc, getZoneColor } from "@/utils/climateZone"
import type { ClimateData } from "@/types/climate"

interface ClimateDataProps {
  data: ClimateData
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = defineProps<ClimateDataProps>()
</script>
<template>
  <div data-cy="lcz-score-popup">
    <div class="flex items-center gap-2 w-full">
      <div
        :style="{ backgroundColor: getZoneColor(props.data.lczIndex) }"
        class="w-4 h-6 rounded"
      ></div>
      <span class="font-accent text-xl" data-cy="lcz-score-popup-title"
        >LCZ {{ props.data.lczIndex }}</span
      >
    </div>
    <div class="w-full text-md mb-2">
      <span data-cy="lcz-score-popup-description">{{ getZoneDesc(props.data.lczIndex) }}</span>
    </div>
  </div>
</template>
