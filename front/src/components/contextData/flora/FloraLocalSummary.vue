<script lang="ts" setup>
import type { LocalFloraSummary } from "@/types/flora"

interface Props {
  summary: LocalFloraSummary
  lczContext: string
}

defineProps<Props>()
</script>

<template>
  <div class="summary-container">
    <div class="stat-row">
      <span class="stat-value">{{ summary.totalSpeciesObserved }}</span>
      <span class="stat-label">espèces végétales observées à proximité</span>
    </div>

    <div v-if="summary.dominantFamilies.length > 0" class="info-block">
      <span class="info-title">Familles dominantes</span>
      <div class="tag-list">
        <span v-for="family in summary.dominantFamilies" :key="family" class="tag">
          {{ family }}
        </span>
      </div>
    </div>

    <div v-if="summary.dominantGenera.length > 0" class="info-block">
      <span class="info-title">Genres dominants</span>
      <div class="tag-list">
        <span v-for="genus in summary.dominantGenera" :key="genus" class="tag">
          {{ genus }}
        </span>
      </div>
    </div>

    <p v-if="lczContext" class="lcz-context">{{ lczContext }}</p>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.summary-container {
  @apply flex flex-col gap-3 p-3 border border-gray-200 rounded-lg;
}

.stat-row {
  @apply flex items-center gap-2;
}

.stat-value {
  @apply text-2xl font-bold text-primary-700;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.info-block {
  @apply flex flex-col gap-1;
}

.info-title {
  @apply text-xs font-medium text-gray-500 uppercase tracking-wide;
}

.tag-list {
  @apply flex flex-wrap gap-1;
}

.tag {
  @apply px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded;
}

.lcz-context {
  @apply text-xs text-gray-500 mt-1 mb-0 italic;
}
</style>
