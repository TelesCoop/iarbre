<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<template>
  <ToggleButton
    :model-value="mapStore.showQPVLayer"
    off-label="Afficher les QPV"
    on-label="Masquer les QPV"
    size="small"
    class="w-fit"
    data-cy="qpv-toggle"
    @update:model-value="mapStore.toggleQPVLayer"
  />
</template>
