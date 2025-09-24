<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <div class="flex items-center gap-2 p-2 md:gap-3 md:p-3">
    <i class="pi pi-building text-primary-500" />
    <span class="text-sm">QPV</span>
    <ToggleSwitch
      :model-value="mapStore.showQPVLayer"
      data-cy="qpv-toggle"
      @update:model-value="mapStore.toggleQPVLayer"
    />
  </div>
</template>
