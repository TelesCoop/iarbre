<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { HOURLY_RASTERS } from "@/utils/hourlyRaster"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"

const mapStore = useMapStore()

const [off, on] = [DataType.PET, DataType.SHADOW]

const isOn = computed(() => mapStore.selectedDataType === on)

const select = (type: DataType) => {
  if (type !== mapStore.selectedDataType) mapStore.changeDataType(type)
}
</script>

<template>
  <div
    class="map-control-panel border-0 w-full grid grid-cols-[1fr_auto_1fr] items-center gap-2.5 text-sm"
    data-cy="hourly-raster-toggle"
  >
    <span
      v-for="(type, index) in [off, on]"
      :id="`hourly-raster-toggle-${type}`"
      :key="type"
      :class="[
        'flex items-center gap-1.5 leading-tight cursor-pointer select-none transition-colors duration-150',
        index === 0 ? 'justify-self-end row-start-1 col-start-1' : 'row-start-1 col-start-3',
        type === mapStore.selectedDataType ? 'text-gray-900' : 'text-gray-500'
      ]"
      @click="select(type)"
    >
      <component
        :is="HOURLY_RASTERS[type]!.icon"
        :class="{ 'text-primary-500': type === mapStore.selectedDataType }"
        :size="16"
        aria-hidden="true"
      />
      <span class="w-min">{{ HOURLY_RASTERS[type]!.toggleLabel }}</span>
    </span>
    <AppToggleSwitch
      :label-id="`hourly-raster-toggle-${on}`"
      :model-value="isOn"
      class="row-start-1 col-start-2"
      @update:model-value="(value) => select(value ? on : off)"
    />
  </div>
</template>
