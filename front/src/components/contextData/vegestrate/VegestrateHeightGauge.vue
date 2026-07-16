<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { ELEVATION_BINS, HEIGHT_CATEGORIES, sqrtPos } from "@/utils/vegetation"

const GAUGE_TICKS = [40, 30, 20, 10, 0].map((value) => ({
  label: `${value} m`,
  position: sqrtPos(value)
}))

const tickStyle = (position: number) => {
  if (position >= 100) return { top: "0" }
  if (position <= 0) return { bottom: "0" }
  return { bottom: `${position}%`, transform: "translateY(50%)" }
}

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
</script>

<template>
  <div class="height-gauge-container vegestrate-panel">
    <div class="vegestrate-summary">
      <svg
        class="vegestrate-tree-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.4"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path
          d="M12 2.5c-3.4 0-6.1 2.6-6.1 5.9 0 2.9 2.1 5.3 4.9 5.8v6.4h2.4v-6.4c2.8-.5 4.9-2.9 4.9-5.8 0-3.3-2.7-5.9-6.1-5.9Z"
        />
      </svg>
      <div class="vegestrate-summary-main">
        <span class="vegestrate-summary-label">Hauteur moyenne</span>
        <div class="flex items-baseline gap-1" aria-live="polite" aria-atomic="true">
          <template v-if="mapStore.vegetationHeightAtPoint === undefined">
            <span class="text-sm text-gray-500">Cliquez sur un pixel.</span>
          </template>
          <template v-else-if="mapStore.vegetationHeightAtPoint != null">
            <span class="text-4xl font-bold leading-none text-primary-800">{{
              formattedHeight
            }}</span>
            <span class="text-xl font-semibold text-primary-800">m</span>
          </template>
          <span v-else class="text-sm text-gray-500">Hors zone</span>
        </div>
      </div>
      <p class="vegestrate-summary-aside">Échelle racine carrée</p>
    </div>

    <div class="vegestrate-legend-card">
      <div class="vegestrate-scale-col relative h-60 text-right">
        <span
          v-for="tick in GAUGE_TICKS"
          :key="tick.label"
          class="absolute right-0 text-sm text-gray-500"
          :style="tickStyle(tick.position)"
          >{{ tick.label }}</span
        >
      </div>
      <div
        role="img"
        aria-label="Échelle de hauteur de végétation de 0 à 40 mètres (échelle racine carrée)"
        class="gauge-bar vegestrate-bar relative transition-opacity duration-300"
        :class="{ 'opacity-40': markerPosition === null }"
        :style="{ background: verticalGradient }"
      >
        <div
          v-if="markerPosition !== null"
          class="gauge-marker absolute inset-x-0 h-[3px] translate-y-1/2 rounded-sm bg-white shadow-[0_0_0_1px_rgba(0,0,0,0.35)]"
          :style="{ bottom: markerPosition + '%' }"
        />
      </div>
      <ul class="vegestrate-categories">
        <li v-for="category in HEIGHT_CATEGORIES" :key="category.label" class="flex flex-col">
          <span class="vegestrate-category-label">{{ category.label }}</span>
          <span class="vegestrate-category-range">{{ category.range }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
