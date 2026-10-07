<script lang="ts" setup>
import { ref } from "vue"
import { useDebounceFn } from "@vueuse/core"
import { useMapStore } from "@/stores/map"
import { HOURS, formatHour } from "@/utils/rasterLayers"

const mapStore = useMapStore()

const hour = ref(mapStore.selectedHour)

const applyHour = useDebounceFn((value: number) => mapStore.setHour(value), 200)

const onHourInput = (event: Event) => {
  hour.value = Number((event.target as HTMLInputElement).value)
  applyHour(hour.value)
}
</script>

<template>
  <label v-if="mapStore.selectedLayer.hourly" class="flex items-center gap-2 text-sm w-full">
    <span class="shrink-0">Heure</span>
    <input
      :value="hour"
      :min="HOURS[0]"
      :max="HOURS[HOURS.length - 1]"
      class="flex-1 accent-primary-500 cursor-pointer"
      data-cy="hour-slider"
      step="1"
      type="range"
      @input="onHourInput"
    />
    <span class="w-8 text-right font-medium tabular-nums">{{ formatHour(hour) }}</span>
  </label>
</template>
