<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { HOURLY_RASTERS, formatHour } from "@/utils/hourlyRaster"
import AppButton from "@/components/shared/AppButton.vue"
import IconSwap from "@/components/icons/IconSwap.vue"

const mapStore = useMapStore()

const target = computed(() =>
  (Object.keys(HOURLY_RASTERS) as DataType[]).find((type) => type !== mapStore.selectedDataType)!
)
</script>

<template>
  <AppButton
    class="self-center px-2.5 py-1 text-xs gap-1 whitespace-nowrap"
    data-cy="hourly-raster-swap"
    size="sm"
    variant="outline"
    @click="mapStore.changeDataType(target)"
  >
    <template #icon-left>
      <IconSwap :size="14" aria-hidden="true" />
    </template>
    Voir {{ HOURLY_RASTERS[target]!.swapLabel }} à {{ formatHour(mapStore.rasterHour) }}
  </AppButton>
</template>
