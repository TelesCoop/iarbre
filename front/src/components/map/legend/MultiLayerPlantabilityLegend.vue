<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

interface Props {
  dataType: DataType
}

const props = defineProps<Props>()
const mapStore = useMapStore()

const handleScoreClick = (score: number) => {
  // Pour le mode multi-calques, nous devons gérer les filtres par calque
  // Pour l'instant, utilisons la logique existante mais l'adapter ultérieurement
  mapStore.toggleAndApplyFilter(score)
}

const SCORE_BG_CLASSES: Record<number, string> = {
  0: "bg-scale-0",
  1: "bg-scale-1",
  2: "bg-scale-2",
  3: "bg-scale-3",
  4: "bg-scale-4",
  5: "bg-scale-5",
  6: "bg-scale-6",
  7: "bg-scale-7",
  8: "bg-scale-8",
  9: "bg-scale-9",
  10: "bg-scale-10"
}
</script>

<template>
  <div
    class="font-accent flex items-center justify-center text-xs leading-3 gap-2 multi-layer-plantability"
    data-cy="multi-layer-plantability-legend"
  >
    <div class="legend-content">
      <div class="legend-title">
        <svg class="legend-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            d="M3 21V5a2 2 0 012-2h6.5l1 1H20a2 2 0 012 2v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          ></path>
        </svg>
        Plantabilité
      </div>
      <div class="legend-scale">
        <span class="scale-label">Non plantable</span>
        <div class="scale-items">
          <score-label
            v-for="index in [0, 2, 4, 6, 8, 10]"
            :key="index"
            :clickable="true"
            :is-selected="mapStore.isFiltered(index)"
            :label="`${index}`"
            :score="index"
            class="scale-item"
            :background-color-class="SCORE_BG_CLASSES[index]"
            @click="handleScoreClick"
          />
        </div>
        <span class="scale-label">Plantable</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-layer-plantability {
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

.legend-scale {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.scale-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.scale-items {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
  justify-content: center;
}

.scale-item {
  transform: scale(0.85);
}

/* Ajustements pour le mode multi-calques */
:deep(.score-label) {
  transform: scale(0.85);
  min-width: 1.5rem;
  height: 1.5rem;
}
</style>
