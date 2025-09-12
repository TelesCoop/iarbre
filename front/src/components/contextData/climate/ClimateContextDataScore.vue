<script lang="ts" setup>
import { computed } from "vue"
import type { ClimateData } from "@/types/climate"
import { CLIMATE_ZONE_COLOR } from "@/utils/climateZone"
import { getAdaptativeColorClass } from "@/utils/color"
import { getZoneColor } from "@/utils/climateZone"

interface ClimateScoreProps {
  data: ClimateData
}

const props = defineProps<ClimateScoreProps>()

const zoneBackgroundColor = computed(() =>
  props.data?.lczIndex ? CLIMATE_ZONE_COLOR[props.data.lczIndex] || "#bcbcbc" : "#bcbcbc"
)
</script>

<template>
  <div
    :class="`map-context-card text-lg ${getAdaptativeColorClass(getZoneColor(props.data.lczIndex))}`"
    :style="{ backgroundColor: zoneBackgroundColor }"
  >
    <span class="text-center"
      >Zone climatique locale : <br />
      {{ props.data.lczDescription }}</span
    >
  </div>
</template>
