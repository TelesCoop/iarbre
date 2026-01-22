<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <div class="flex items-center gap-2 p-3 bg-white rounded-lg">
    <i class="pi pi-building text-primary-500" />
    <span class="text-sm font-sans">QPV</span>
    <ToggleSwitch
      :model-value="mapStore.showQPVLayer"
      data-cy="qpv-toggle"
      @update:model-value="mapStore.toggleQPVLayer"
    />
  </div>
</template>
