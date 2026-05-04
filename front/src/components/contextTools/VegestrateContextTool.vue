<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { VegestrateMode, VegestrateModeToLabel } from "@/utils/vegetation"
import AppSelect from "@/components/shared/AppSelect.vue"

const mapStore = useMapStore()

const options = Object.values(VegestrateMode).map((mode) => ({
  label: VegestrateModeToLabel[mode],
  value: mode
}))

const onModeChange = (value: string | number) => {
  mapStore.vegestrateMode = value as VegestrateMode
  mapStore.refreshDatatype()
}
</script>

<template>
  <div class="context-menu-tools map-control-panel">
    <AppSelect
      :model-value="mapStore.vegestrateMode"
      :options="options"
      option-label="label"
      option-value="value"
      @update:model-value="onModeChange"
    />
  </div>
</template>
