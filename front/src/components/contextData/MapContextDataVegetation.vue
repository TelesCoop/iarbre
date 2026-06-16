<script lang="ts" setup>
import { computed } from "vue"
import { type VegetationData } from "@/types/vegetation"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import { useMapStore } from "@/stores/map"
import VegestrateContextDataInfo from "./vegestrate/VegestrateContextDataInfo.vue"
import { ELEVATION_BINS, ELEVATION_LABEL_STOPS, sqrtPos } from "@/utils/vegetation"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface VegetationCardProps {
  data?: VegetationData | null
}

const props = withDefaults(defineProps<VegetationCardProps>(), {
  data: null
})

const currentData = computed<VegetationData | null>(() => props.data ?? null)

const heightDisplayData = computed(() =>
  mapStore.vegetationHeightAtPoint !== undefined
    ? { height: mapStore.vegetationHeightAtPoint }
    : null
)

const displayData = computed(() =>
  mapStore.showVegestrateHeight ? heightDisplayData.value : currentData.value
)

const emptyMessage = computed(() =>
  mapStore.showVegestrateHeight ? "Cliquez sur un pixel." : "Cliquez sur un carreau."
)

const verticalGradient = `linear-gradient(to top, ${ELEVATION_BINS.map((b) => `${b.color} ${sqrtPos(b.min)}%`).join(", ")})`

const markerPosition = computed(() => {
  const h = heightDisplayData.value?.height
  if (h == null) return null
  return sqrtPos(Math.min(h, 40))
})

const formattedHeight = computed(() => {
  const h = heightDisplayData.value?.height
  if (h == null) return null
  return h.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
})

const gaugeAriaLabel = computed(() => {
  const h = heightDisplayData.value?.height
  if (h == null)
    return "Jauge de hauteur de végétation (0-40 m, échelle racine carrée), aucune donnée"
  return `Jauge de hauteur de végétation (0-40 m, échelle racine carrée), valeur : ${formattedHeight.value} m`
})
</script>

<template>
  <ContextDataMainContainer
    color-scheme="vegetation"
    title="Végétation"
    description="Données de végétation issues de la fusion de la classification du LIDAR 2023 et de la classification des orthophotos à l'aide de FLAIR-HUB de l'IGN."
    :data="displayData"
    :empty-message="emptyMessage"
    :zoom-level="zoomLevel"
  >
    <template #content>
      <div v-if="mapStore.showVegestrateHeight" class="height-gauge-container">
        <p class="gauge-legend">Hauteur de végétation</p>
        <p class="gauge-subtitle">Échelle racine carrée</p>
        <div class="gauge-row" :class="{ 'gauge-row--idle': markerPosition === null }">
          <div
            role="img"
            :aria-label="gaugeAriaLabel"
            class="gauge-bar"
            :class="{ 'gauge-bar--idle': markerPosition === null }"
            :style="{ background: verticalGradient }"
          >
            <div
              v-if="markerPosition !== null"
              class="gauge-marker"
              :style="{ bottom: markerPosition + '%' }"
            />
          </div>
          <div class="gauge-ticks">
            <span
              v-for="stop in [...ELEVATION_LABEL_STOPS].reverse()"
              :key="stop.label"
              class="gauge-tick"
              :style="{ bottom: stop.position + '%' }"
              >{{ stop.label }}</span
            >
          </div>
          <div class="height-value" aria-live="polite" aria-atomic="true">
            <template v-if="heightDisplayData?.height != null">
              <span class="height-number">{{ formattedHeight }}</span>
              <span class="height-unit">m</span>
            </template>
            <span v-else class="height-empty">Hors zone</span>
          </div>
        </div>
      </div>
      <VegestrateContextDataInfo v-else-if="currentData" :data="currentData" />
    </template>
  </ContextDataMainContainer>
</template>

<style scoped>
@reference "@/styles/main.css";

.height-gauge-container {
  @apply flex flex-col items-center gap-2 p-4;
}

.gauge-legend {
  @apply text-xs text-gray-600 uppercase tracking-wide;
}

.gauge-subtitle {
  @apply text-xs text-gray-600;
}

.gauge-row {
  @apply flex items-stretch gap-3;
  height: 180px;
}

.gauge-bar {
  @apply relative rounded-full transition-opacity duration-300;
  width: 1.25rem;
}

.gauge-bar--idle {
  @apply opacity-40;
}

.gauge-row--idle .gauge-ticks {
  @apply opacity-40 transition-opacity duration-300;
}

@media (prefers-reduced-motion: reduce) {
  .gauge-bar,
  .gauge-row--idle .gauge-ticks {
    transition: none;
  }
}

.gauge-marker {
  @apply absolute left-0 right-0 bg-white rounded-sm;
  height: 3px;
  transform: translateY(50%);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.35);
}

.gauge-ticks {
  @apply relative;
  width: 2rem;
}

.gauge-tick {
  @apply absolute text-xs text-gray-600;
  transform: translateY(50%);
}

.height-value {
  @apply self-center flex items-baseline gap-1 min-w-[3.5rem];
}

.height-number {
  @apply text-3xl font-bold text-primary-800;
}

.height-unit {
  @apply text-sm font-normal text-primary-600;
}

.height-empty {
  @apply text-xs text-gray-600;
}
</style>
