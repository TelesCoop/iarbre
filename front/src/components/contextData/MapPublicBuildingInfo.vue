<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { PublicBuildingCategoryToLabel } from "@/utils/enum"
import IconPublicBuilding from "@/components/icons/IconPublicBuilding.vue"

const mapStore = useMapStore()
const building = computed(() => mapStore.selectedPublicBuilding)

const title = computed(() => building.value?.name || building.value?.nature)
const nature = computed(() => building.value?.natureDetaillee || building.value?.nature)
</script>

<template>
  <div v-if="building" class="map-control-panel" data-cy="public-building-info">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <IconPublicBuilding class="text-primary-500 shrink-0" :size="16" aria-hidden="true" />
        <span class="text-sm font-medium font-sans">{{ title }}</span>
      </div>
      <MapControlButton
        aria-label="Fermer"
        class="w-7 h-7 text-gray-400 hover:text-gray-600 hover:bg-gray-100 hover:border-gray-200"
        size="sm"
        @click="mapStore.clearPublicBuildingSelection()"
      >
        <IconClose :size="12" />
      </MapControlButton>
    </div>
    <div class="info-section">
      <div class="info-row">
        <span class="info-label">Catégorie</span>
        <span class="info-value">{{ PublicBuildingCategoryToLabel[building.category] }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Type</span>
        <span class="info-value">{{ nature }}</span>
      </div>
      <div v-if="building.studentCount" class="info-row">
        <span class="info-label">Élèves</span>
        <span class="info-value">{{ building.studentCount.toLocaleString("fr-FR") }}</span>
      </div>
      <div v-if="building.capacity" class="info-row">
        <span class="info-label">Places d'accueil</span>
        <span class="info-value">{{ building.capacity.toLocaleString("fr-FR") }}</span>
      </div>
      <div v-if="building.educationPriority" class="info-row">
        <span class="info-label">Éducation prioritaire</span>
        <span class="info-value">{{ building.educationPriority }}</span>
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
  @apply flex items-center justify-between gap-4;
}

.info-label {
  @apply text-xs font-sans text-gray-500;
}

.info-value {
  @apply text-xs font-sans font-medium text-gray-800 text-right;
}
</style>
