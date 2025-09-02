<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <div class="hidden md:flex items-center gap-3 p-3">
    <i class="pi pi-building text-primary-500" />
    <span class="text-sm">QPV</span>
    <ToggleSwitch
      :model-value="mapStore.showQPVLayer"
      data-cy="qpv-toggle"
      @update:model-value="mapStore.toggleQPVLayer"
    />
  </div>
</template>
