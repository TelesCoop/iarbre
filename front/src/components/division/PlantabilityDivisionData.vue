<script lang="ts" setup>
import { computed } from "vue"
import type { City, Iris } from "@/types/division"

interface DivisionDataProps {
  cities?: City[]
  irisList?: Iris[]
}

const props = withDefaults(defineProps<DivisionDataProps>(), {
  cities: () => [],
  irisList: () => []
})

const hasCities = computed(() => props.cities && props.cities.length > 0)
const hasIris = computed(() => props.irisList && props.irisList.length > 0)

const formatScore = (value: number | null) => {
  if (value === null) return "-"
  return value.toFixed(1)
}

const getScoreClass = (value: number | null) => {
  if (value === null) return ""
  if (value >= 7) return "score-high"
  if (value >= 4) return "score-medium"
  return "score-low"
}
</script>

<template>
  <div class="division-data">
    <!-- Communes Section -->
    <div v-if="hasCities" class="section">
      <div class="section-header">
        <span class="section-icon">🏛️</span>
        <span class="section-title">Communes</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">Nom</th>
            <th class="col-code">Code INSEE</th>
            <th class="col-score">Score</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(city, index) in props.cities"
            :key="`city-${city.id}`"
            :class="{ 'row-border': index < props.cities.length - 1 }"
          >
            <td class="cell-name">{{ city.name || "-" }}</td>
            <td class="cell-code">{{ city.code }}</td>
            <td :class="['cell-score', getScoreClass(city.averageNormalizedIndice)]">
              {{ formatScore(city.averageNormalizedIndice) }}
              <span class="score-max">/10</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- IRIS Section -->
    <div v-if="hasIris" class="section">
      <div class="section-header">
        <span class="section-icon">📍</span>
        <span class="section-title">IRIS</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">Nom</th>
            <th class="col-code">Code</th>
            <th class="col-score">Score</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(iris, index) in props.irisList"
            :key="`iris-${iris.id}`"
            :class="{ 'row-border': index < props.irisList.length - 1 }"
          >
            <td class="cell-name">{{ iris.name || "-" }}</td>
            <td class="cell-code">{{ iris.code }}</td>
            <td :class="['cell-score', getScoreClass(iris.averageNormalizedIndice)]">
              {{ formatScore(iris.averageNormalizedIndice) }}
              <span class="score-max">/10</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!hasCities && !hasIris" class="empty-state">
      Aucune donnée disponible pour cette zone
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.division-data {
  @apply flex flex-col gap-4;
}

.section {
  @apply flex flex-col;
}

.section-header {
  @apply flex items-center gap-2 py-2 px-2.5 bg-gray-100 border border-gray-200 border-b-0 rounded-t-md;
}

.section-icon {
  @apply text-sm;
}

.section-title {
  @apply text-sm font-semibold text-gray-800;
}

.data-table {
  @apply w-full bg-white border border-gray-200 rounded-b-md overflow-hidden text-sm;
}

.data-table th {
  @apply py-2 px-2.5 text-left font-medium text-gray-500 bg-gray-50 border-b border-gray-200;
}

.data-table td {
  @apply py-2 px-2.5;
}

.row-border {
  @apply border-b border-gray-100;
}

.col-name {
  @apply w-[45%];
}

.col-code {
  @apply w-[30%];
}

.col-score {
  @apply w-[25%] text-right;
}

.cell-name {
  @apply font-medium text-gray-700;
}

.cell-code {
  @apply font-mono text-xs text-gray-500;
}

.cell-score {
  @apply font-semibold;
}

.score-max {
  @apply text-xs font-normal text-gray-400 ml-0.5;
}

.score-high {
  @apply text-green-600;
}

.score-medium {
  @apply text-yellow-600;
}

.score-low {
  @apply text-orange-600;
}

.empty-state {
  @apply py-8 text-center text-gray-500 text-sm;
}
</style>
