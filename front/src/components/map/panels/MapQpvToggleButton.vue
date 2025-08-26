<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <div class="flex items-center gap-3 bg-white p-3">
    <i class="pi pi-building text-primary-500" />
    <span class="text-sm font-medium">QPV</span>
    <ToggleSwitch
      :model-value="mapStore.showQPVLayer"
      class="ml-auto"
      data-cy="qpv-toggle"
      @update:model-value="mapStore.toggleQPVLayer"
    />
  </div>
</template>
