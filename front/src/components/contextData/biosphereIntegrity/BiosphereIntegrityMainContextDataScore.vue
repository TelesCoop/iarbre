<script lang="ts" setup>
import { computed } from "vue"
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import { getAdaptativeColorClass } from "@/utils/color"
import { getZoneColor, CLIMATE_ZONE_COLOR } from "@/utils/climateZone"

interface BiosphereIntegrityMainScoreProps {
  data: BiosphereIntegrityData
}

const props = defineProps<BiosphereIntegrityMainScoreProps>()
</script>
<template>
  <CircularScore
    :score="data.indice"
    :max-score="100"
    :percentage="data.indice"
    name="IFB"
    label="ifb"
    color-scheme="biosphereIntegrity"
  />
</template>
