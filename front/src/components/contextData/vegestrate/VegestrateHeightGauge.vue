<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { ELEVATION_BINS, HEIGHT_CATEGORIES, sqrtPos } from "@/utils/vegetation"
import VegestratePanel from "@/components/contextData/vegestrate/VegestratePanel.vue"

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
  <VegestratePanel
    class="height-gauge-container"
    summary-label="Hauteur moyenne"
    aside-note="Échelle racine carrée"
    bar-aria-label="Échelle de hauteur de végétation de 0 à 40 mètres (échelle racine carrée)"
    :bar-background="verticalGradient"
    :bar-class="[
      'gauge-bar transition-opacity duration-300',
      { 'opacity-40': markerPosition === null }
    ]"
    :categories="HEIGHT_CATEGORIES"
  >
    <template #value>
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
    </template>

    <template #scale>
      <span
        v-for="tick in GAUGE_TICKS"
        :key="tick.label"
        class="absolute right-0 text-sm text-gray-500"
        :style="tickStyle(tick.position)"
        >{{ tick.label }}</span
      >
    </template>

    <template #bar>
      <div
        v-if="markerPosition !== null"
        class="gauge-marker absolute inset-x-0 h-[3px] translate-y-1/2 rounded-sm bg-white shadow-[0_0_0_1px_rgba(0,0,0,0.35)]"
        :style="{ bottom: markerPosition + '%' }"
      />
    </template>
  </VegestratePanel>
</template>
