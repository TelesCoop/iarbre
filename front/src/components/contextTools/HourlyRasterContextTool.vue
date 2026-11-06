<script lang="ts" setup>
import { computed, ref } from "vue"
import { useDebounceFn } from "@vueuse/core"
import { useMapStore } from "@/stores/map"
import { HOURLY_RASTERS, HOURS, formatHour, type Hour } from "@/utils/hourlyRaster"

const mapStore = useMapStore()

const years = computed(() => HOURLY_RASTERS[mapStore.selectedDataType]?.years)

const hour = ref<number>(mapStore.rasterHour)

const applyHour = useDebounceFn((value: Hour) => mapStore.setRasterHour(value), 200)

const onHourInput = (event: Event) => {
  hour.value = Number((event.target as HTMLInputElement).value)
  applyHour(hour.value as Hour)
}
</script>

<template>
  <div v-if="years" class="map-control-panel border-0">
    <div class="flex items-center gap-1" role="radiogroup" aria-label="Scénario">
      <button
        v-for="year in years"
        :key="year"
        :class="['layer-chip', { active: mapStore.rasterYear === year }]"
        :aria-checked="mapStore.rasterYear === year"
        :data-cy="`raster-year-${year}`"
        role="radio"
        type="button"
        @click="mapStore.rasterYear !== year && mapStore.setRasterYear(year)"
      >
        {{ year }}
      </button>
    </div>
  </div>

  <label class="w-full flex items-center gap-2 px-2 py-3 bg-white rounded-lg text-sm">
    <span class="shrink-0">Heure</span>
    <input
      :value="hour"
      :min="HOURS[0]"
      :max="HOURS[HOURS.length - 1]"
      class="flex-1 accent-primary-500 cursor-pointer"
      data-cy="raster-hour-slider"
      step="1"
      type="range"
      @input="onHourInput"
    />
    <span class="w-8 text-right font-medium tabular-nums">{{ formatHour(hour) }}</span>
  </label>
</template>
