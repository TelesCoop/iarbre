<script lang="ts" setup>
import { computed } from "vue"
import type { ClimateData } from "@/types/climate"
import { getContrastTextHex } from "@/utils/color"
import { CLIMATE_ZONE_COLOR } from "@/utils/climateZone"
import ContextDataScoreHeader from "@/components/contextData/shared/ContextDataScoreHeader.vue"

interface ClimateScoreProps {
  data: ClimateData
}

const props = defineProps<ClimateScoreProps>()

const zoneColor = computed(() => CLIMATE_ZONE_COLOR[props.data?.lczIndex] || "#D1D5DB")

const zoneTextColor = computed(() => getContrastTextHex(zoneColor.value))

const zoneLabel = computed(() => String(props.data?.lczIndex ?? "-"))

const zoneDescription = computed(() => props.data?.lczDescription || "Description non disponible")
</script>

<template>
  <div data-cy="climate-context-data-score">
    <ContextDataScoreHeader
      :swatch-color="zoneColor"
      :swatch-label="zoneLabel"
      :swatch-text-color="zoneTextColor"
      :title="zoneDescription"
      eyebrow="Zone climatique locale"
    />
  </div>
</template>
