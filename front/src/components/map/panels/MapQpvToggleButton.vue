<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <div class="flex items-center gap-3 bg-white p-3">
    <i class="pi pi-building text-primary-500" />
    <ToggleSwitch
      :model-value="mapStore.showQPVLayer"
      data-cy="qpv-toggle"
      @update:model-value="mapStore.toggleQPVLayer"
    />
    <span class="text-sm font-medium">Quartier Prioritaires de la Ville</span>
  </div>
</template>
