<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"

const mapStore = useMapStore()
const parcel = computed(() => mapStore.selectedCadastreParcel)

const formattedSurface = computed(() => {
  if (!parcel.value?.surface) return "N/A"
  return `${parcel.value.surface.toLocaleString("fr-FR")} m²`
})
</script>

<template>
  <div v-if="parcel" class="map-control-panel" data-cy="cadastre-parcel-info">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <IconMap class="text-primary-500 shrink-0" :size="16" aria-hidden="true" />
        <span class="text-sm font-medium font-sans">
          Parcelle {{ parcel.section }}{{ parcel.numero }}
        </span>
      </div>
      <MapControlButton
        aria-label="Fermer"
        class="w-7 h-7 text-gray-400 hover:text-gray-600 hover:bg-gray-100 hover:border-gray-200"
        size="sm"
        @click="mapStore.clearCadastreSelection()"
      >
        <IconClose :size="12" />
      </MapControlButton>
    </div>
    <div class="info-section">
      <div class="info-row">
        <span class="info-label">Surface</span>
        <span class="info-value">{{ formattedSurface }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.info-section {
  @apply flex flex-col gap-1 mt-2 pt-2 border-t border-gray-100;
}

.info-row {
  @apply flex items-center justify-between;
}

.info-label {
  @apply text-xs font-sans text-gray-500;
}

.info-value {
  @apply text-xs font-sans font-medium text-gray-800;
}
</style>
