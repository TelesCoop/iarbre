<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { PublicBuildingCategoryToLabel } from "@/utils/enum"
import IconPublicBuilding from "@/components/icons/IconPublicBuilding.vue"
import type { MapFeatureInfoRow } from "@/components/contextData/shared/MapFeatureInfoCard.vue"

const mapStore = useMapStore()
const building = computed(() => mapStore.selectedPublicBuilding)

const rows = computed<MapFeatureInfoRow[]>(() => {
  if (!building.value) return []
  const { category, nature, natureDetaillee, studentCount, capacity, educationPriority } =
    building.value
  return [
    { label: "Catégorie", value: PublicBuildingCategoryToLabel[category] },
    { label: "Type", value: natureDetaillee || nature },
    studentCount && { label: "Élèves", value: studentCount.toLocaleString("fr-FR") },
    capacity && { label: "Places d'accueil", value: capacity.toLocaleString("fr-FR") },
    educationPriority && { label: "Éducation prioritaire", value: educationPriority }
  ].filter((row): row is MapFeatureInfoRow => Boolean(row))
})
</script>

<template>
  <MapFeatureInfoCard
    v-if="building"
    :title="building.name || building.nature"
    :rows="rows"
    data-cy="public-building-info"
    @close="mapStore.clearPublicBuildingSelection()"
  >
    <template #icon>
      <IconPublicBuilding class="text-primary-500 shrink-0" :size="16" aria-hidden="true" />
    </template>
  </MapFeatureInfoCard>
</template>
