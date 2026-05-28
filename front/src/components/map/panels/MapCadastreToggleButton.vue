<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"

const mapStore = useMapStore()

const isActive = computed({
  get: () => mapStore.showCadastreLayer,
  set: () => mapStore.toggleCadastreLayer()
})
</script>

<template>
  <div
    class="map-control-panel flex items-center gap-2 cursor-pointer select-none px-2 py-2 min-h-11"
    @click="isActive = !isActive"
  >
    <IconMap class="text-primary-500" :size="16" aria-hidden="true" />
    <span id="cadastre-label" class="text-sm font-sans">Cadastre</span>
    <AppToggleSwitch
      v-model="isActive"
      data-cy="cadastre-toggle"
      label-id="cadastre-label"
      @click.stop
    />
  </div>
</template>
