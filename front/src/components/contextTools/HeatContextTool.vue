<script lang="ts" setup>
import { computed, ref } from "vue"
import { useDebounceFn } from "@vueuse/core"
import { useMapStore } from "@/stores/map"
import { HEAT_HOURS, HeatMode, HeatModeToLabel, formatHeatHour, isHourlyMode } from "@/utils/heat"
import AppSelect from "@/components/shared/AppSelect.vue"

const mapStore = useMapStore()

const options = Object.values(HeatMode).map((mode) => ({
  label: HeatModeToLabel[mode],
  value: mode
}))

const hour = ref(mapStore.heatHour)
const showHourSlider = computed(() => isHourlyMode(mapStore.heatMode))

const onModeChange = (value: string | number) => {
  mapStore.setHeatMode(value as HeatMode)
}

const applyHour = useDebounceFn((value: number) => mapStore.setHeatHour(value), 200)

const onHourInput = (event: Event) => {
  hour.value = Number((event.target as HTMLInputElement).value)
  applyHour(hour.value)
}
</script>

<template>
  <div class="context-menu-tools map-control-panel flex flex-col gap-2" data-cy="heat-context-tool">
    <AppSelect
      :model-value="mapStore.heatMode"
      :options="options"
      option-label="label"
      option-value="value"
      @update:model-value="onModeChange"
    />
    <label v-if="showHourSlider" class="flex items-center gap-2 text-sm">
      <span class="shrink-0">Heure</span>
      <input
        :value="hour"
        :min="HEAT_HOURS[0]"
        :max="HEAT_HOURS[HEAT_HOURS.length - 1]"
        class="flex-1 accent-primary-500 cursor-pointer"
        data-cy="heat-hour-slider"
        step="1"
        type="range"
        @input="onHourInput"
      />
      <span class="w-8 text-right font-medium tabular-nums">{{ formatHeatHour(hour) }}</span>
    </label>
  </div>
</template>
