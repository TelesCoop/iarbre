<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { ELEVATION_BINS, ELEVATION_LABEL_STOPS, sqrtPos } from "@/utils/vegetation"

const REVERSED_STOPS = [...ELEVATION_LABEL_STOPS].reverse()

const verticalGradient = `linear-gradient(to top, ${ELEVATION_BINS.map((b) => `${b.color} ${sqrtPos(b.min)}%`).join(", ")})`

const mapStore = useMapStore()

const markerPosition = computed(() => {
  const h = mapStore.vegetationHeightAtPoint
  if (h == null) return null
  return sqrtPos(Math.min(h, 40))
})

const formattedHeight = computed(() => {
  const h = mapStore.vegetationHeightAtPoint
  if (h == null) return null
  return h.toLocaleString("fr-FR", { maximumFractionDigits: 1 })
})

const gaugeAriaLabel = computed(() => {
  const h = mapStore.vegetationHeightAtPoint
  if (h == null)
    return "Jauge de hauteur de végétation (0-40 m, échelle racine carrée), aucune donnée"
  return `Jauge de hauteur de végétation (0-40 m, échelle racine carrée), valeur : ${formattedHeight.value} m`
})
</script>

<template>
  <div class="height-gauge-container">
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
          v-for="stop in REVERSED_STOPS"
          :key="stop.label"
          class="gauge-tick"
          :style="{ bottom: stop.position + '%' }"
          >{{ stop.label }}</span
        >
      </div>
      <div class="height-value" aria-live="polite" aria-atomic="true">
        <template v-if="mapStore.vegetationHeightAtPoint != null">
          <span class="height-number">{{ formattedHeight }}</span>
          <span class="height-unit">m</span>
        </template>
        <span v-else class="height-empty">Hors zone</span>
      </div>
    </div>
  </div>
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
