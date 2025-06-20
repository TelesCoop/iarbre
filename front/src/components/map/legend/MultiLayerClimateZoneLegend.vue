<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2 multi-layer-climate"
    data-cy="multi-layer-climate-zones-legend"
  >
    <div class="legend-content">
      <div class="legend-title">
        <svg class="legend-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          ></path>
        </svg>
        Zone climatique
      </div>
      <div class="zone-grid">
        <div v-for="(zone, index) in zones" :key="index" class="zone-item">
          <ClimateZoneScoreLabel
            :zone="zone"
            size="compact"
            class="zone-label"
            @click="handleZoneClick(zone)"
          />
        </div>
      </div>
    </div>
    <ExpandToggle :is-expanded="isExpanded" @toggle="isExpanded = !isExpanded" />
    <div v-if="isExpanded" class="flex flex-col items-start mt-2 gap-1 text-xs">
      <div
        v-for="(zone, index) in zones"
        :key="'vertical-' + index"
        class="flex items-center gap-2"
      >
        <ClimateZoneScoreLabel
          :zone="zone"
          size="detailed"
          class="scale-90"
          @click="handleZoneClick(zone)"
        />
        <span class="text-xs">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc } from "@/utils/climateZone"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import ClimateZoneScoreLabel from "@/components/map/score/ClimateZoneScoreLabel.vue"
import ExpandToggle from "../../toggle/ExpandToggle.vue"

interface Props {
  dataType: DataType
}

const props = defineProps<Props>()

const isExpanded = ref(false)
const mapStore = useMapStore()

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

const handleZoneClick = (zone: string) => {
  // Pour le mode multi-calques, nous devons gérer les filtres par calque
  // Pour l'instant, utilisons la logique existante mais l'adapter ultérieurement
  mapStore.toggleAndApplyFilter(zone)
}
</script>

<style scoped>
.multi-layer-climate {
  padding: 0.75rem;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

/* Nouveau style harmonisé avec le contexte panel */
.legend-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.legend-icon {
  width: 0.75rem;
  height: 0.75rem;
  color: #6b7280;
}

.zone-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  justify-content: center;
  align-items: center;
}

.zone-item {
  display: flex;
  align-items: center;
}

.zone-label {
  transform: scale(0.85);
}

/* Ajustements pour le mode multi-calques */
:deep(.climate-zone-label) {
  transform: scale(0.85);
}
</style>
