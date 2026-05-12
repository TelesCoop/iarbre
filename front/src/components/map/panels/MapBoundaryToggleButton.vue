<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconBoundary from "@/components/icons/IconBoundary.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"

const mapStore = useMapStore()

const isActive = computed({
  get: () => mapStore.showBoundaryLayer,
  set: () => mapStore.toggleBoundaryLayer()
})
</script>

<template>
  <div
    class="map-control-panel flex items-center gap-2 cursor-pointer select-none px-2 py-2 min-h-11"
    @click="isActive = !isActive"
  >
    <IconBoundary class="text-primary-500" :size="16" aria-hidden="true" />
    <span id="boundary-label" class="text-sm font-sans">Communes</span>
    <AppToggleSwitch
      v-model="isActive"
      data-cy="boundary-toggle"
      label-id="boundary-label"
      @click.stop
    />
  </div>
</template>
