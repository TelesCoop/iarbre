<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconBuilding from "@/components/icons/IconBuilding.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"

const mapStore = useMapStore()

const isActive = computed({
  get: () => mapStore.showQPVLayer,
  set: () => mapStore.toggleQPVLayer()
})
</script>

<template>
  <div
    class="map-control-panel flex items-center gap-2 cursor-pointer select-none px-2 py-2 min-h-11"
    @click="isActive = !isActive"
  >
    <IconBuilding class="text-primary-500" :size="16" aria-hidden="true" />
    <span id="qpv-label" class="text-sm font-sans">QPV</span>
    <AppToggleSwitch v-model="isActive" data-cy="qpv-toggle" label-id="qpv-label" @click.stop />
  </div>
</template>
