<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { compassPoint, formatHour, simulationSunAzimuth } from "@/utils/hourlyRaster"

const mapStore = useMapStore()

const azimuth = computed(() => simulationSunAzimuth(mapStore.rasterHour))

const direction = computed(() => {
  const point = compassPoint(azimuth.value)
  return point.charAt(0).toUpperCase() + point.slice(1)
})

const hour = computed(() => formatHour(mapStore.rasterHour))

const label = computed(
  () =>
    `Soleil : ${direction.value.toLowerCase()} à ${hour.value} (azimut ${Math.round(azimuth.value)}°)`
)
</script>

<template>
  <div
    :aria-label="label"
    class="flex items-center justify-center gap-2"
    data-cy="sun-compass"
    role="img"
  >
    <svg aria-hidden="true" class="shrink-0 w-11 h-11" viewBox="0 0 56 56">
      <circle cx="28" cy="28" fill="white" r="22" stroke="#d1d5db" stroke-width="1.5" />
      <g :transform="`rotate(${-mapStore.currentBearing} 28 28)`">
        <text fill="#374151" font-size="9" font-weight="700" text-anchor="middle" x="28" y="15">
          N
        </text>
      </g>
      <g
        :transform="`rotate(${azimuth - mapStore.currentBearing} 28 28)`"
        data-cy="sun-compass-sun"
      >
        <path d="M28 28V11" stroke="#4b5563" stroke-linecap="round" stroke-width="2" />
        <circle cx="28" cy="6" fill="#f59e0b" r="5" stroke="white" stroke-width="1.5" />
      </g>
      <circle cx="28" cy="28" fill="#4b5563" r="2" />
    </svg>
    <div class="flex flex-col w-24 leading-tight">
      <span class="text-xs font-medium text-gray-500 uppercase tracking-tight">Soleil</span>
      <span class="text-sm font-bold text-gray-800">{{ direction }}</span>
    </div>
  </div>
</template>
