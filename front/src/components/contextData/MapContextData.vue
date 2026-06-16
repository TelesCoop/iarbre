<script lang="ts" setup>
import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type { VegetationData } from "@/types/vegetation"
import ContextDataSkeleton from "@/components/contextData/shared/ContextDataSkeleton.vue"
import AppButton from "@/components/shared/AppButton.vue"
import IconInfo from "@/components/icons/IconInfo.vue"
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"

const mapStore = useMapStore()
const zoneStore = useZoneStore()
const router = useRouter()

defineProps({
  fullHeight: {
    type: Boolean,
    default: false
  }
})

const goToZoneDashboard = () => {
  const polygon = mapStore.getDrawnPolygon()
  if (!polygon) return
  zoneStore.setZone(polygon)
  router.push({ name: "dashboard" })
}
</script>

<template>
  <div class="map-context-data-container w-full flex flex-col min-h-0" data-cy="map-context-data">
    <ContextDataSkeleton v-if="mapStore.isCalculating" />
    <div
      v-else-if="mapStore.contextData.error"
      class="context-error"
      data-cy="context-data-error"
      role="alert"
    >
      <span class="context-error-icon" aria-hidden="true">
        <IconInfo :size="22" />
      </span>
      <p class="context-error-text">
        Impossible de récupérer les données pour cette zone. Vérifiez votre connexion, puis
        réessayez.
      </p>
      <AppButton
        data-cy="context-data-retry"
        size="sm"
        variant="outline"
        @click="mapStore.contextData.retry()"
      >
        Réessayer
      </AppButton>
    </div>
    <template v-else>
      <MapContextDataPlantability
        v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
        :data="mapStore.contextData.data as PlantabilityData"
      />
      <MapContextDataVulnerability
        v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
        :data="mapStore.contextData.data as VulnerabilityData"
      />
      <MapContextDataClimateZone
        v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
        :data="mapStore.contextData.data as ClimateData"
      />
      <map-context-data-biosphere-integrity
        v-else-if="mapStore.selectedDataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY"
        :data="mapStore.contextData.data as BiosphereIntegrityData"
      />
      <MapContextDataPlantabilityVulnerability
        v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
        :data="mapStore.contextData.data as PlantabilityVulnerabilityData"
      />
      <map-context-data-vegetation
        v-if="mapStore.selectedDataType === DataType.VEGESTRATE"
        :data="mapStore.contextData.data as VegetationData"
      />
    </template>

    <AppButton
      v-if="mapStore.hasShapeContextData"
      class="zone-dashboard-cta"
      variant="primary"
      full-width
      data-cy="zone-dashboard-cta"
      @click="goToZoneDashboard"
    >
      Voir le tableau de bord de cette zone
    </AppButton>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.zone-dashboard-cta {
  @apply mt-4 shrink-0;
}

.context-error {
  @apply flex flex-col items-center justify-center gap-3 h-full;
  @apply px-6 py-8 text-center;
  @apply rounded-xl border border-dashed border-orange-200 bg-orange-50;
}

.context-error-icon {
  @apply flex items-center justify-center shrink-0;
  @apply w-11 h-11 rounded-full bg-white text-orange-500;
}

.context-error-text {
  @apply max-w-64 text-sm font-medium leading-snug text-gray-600;
}
</style>
