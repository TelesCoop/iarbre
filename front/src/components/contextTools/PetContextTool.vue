<script lang="ts" setup>
import { ref } from "vue"
import { useDebounceFn } from "@vueuse/core"
import { useMapStore } from "@/stores/map"
import { PET_HOURS, PET_YEARS, formatHour, type PetHour } from "@/utils/pet"

const mapStore = useMapStore()

const hour = ref<number>(mapStore.petHour)

const applyHour = useDebounceFn((value: PetHour) => mapStore.setPetHour(value), 200)

const onHourInput = (event: Event) => {
  hour.value = Number((event.target as HTMLInputElement).value)
  applyHour(hour.value as PetHour)
}
</script>

<template>
  <div class="map-control-panel border-0">
    <div class="flex items-center gap-1" role="radiogroup" aria-label="Scénario PET">
      <button
        v-for="year in PET_YEARS"
        :key="year"
        :class="['layer-chip', { active: mapStore.petYear === year }]"
        :aria-checked="mapStore.petYear === year"
        :data-cy="`pet-year-${year}`"
        role="radio"
        type="button"
        @click="mapStore.petYear !== year && mapStore.setPetYear(year)"
      >
        {{ year }}
      </button>
    </div>
  </div>

  <label class="map-control-panel w-full border-0 flex items-center gap-2 text-sm">
    <span class="shrink-0">Heure</span>
    <input
      :value="hour"
      :min="PET_HOURS[0]"
      :max="PET_HOURS[PET_HOURS.length - 1]"
      class="flex-1 accent-primary-500 cursor-pointer"
      data-cy="pet-hour-slider"
      step="1"
      type="range"
      @input="onHourInput"
    />
    <span class="w-8 text-right font-medium tabular-nums">{{ formatHour(hour) }}</span>
  </label>
</template>
