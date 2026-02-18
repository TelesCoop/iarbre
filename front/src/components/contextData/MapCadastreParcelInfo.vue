<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"
import IconClose from "@/components/icons/IconClose.vue"

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
      <button class="close-btn" aria-label="Fermer" @click="mapStore.clearCadastreSelection()">
        <IconClose :size="12" />
      </button>
    </div>
    <div class="info-section">
      <div class="info-row">
        <span class="info-label">Identifiant</span>
        <span class="info-value">{{ parcel.parcelId }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Surface</span>
        <span class="info-value">{{ formattedSurface }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.close-btn {
  @apply w-7 h-7 flex items-center justify-center shrink-0;
  @apply rounded-full text-gray-400;
  @apply hover:text-gray-600 hover:bg-gray-100;
  @apply transition-colors duration-200;
}

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
