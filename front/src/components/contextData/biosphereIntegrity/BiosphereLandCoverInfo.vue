<script lang="ts" setup>
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"

interface BiosphereLandCoverInfoProps {
  data: BiosphereIntegrityData
}

const props = defineProps<BiosphereLandCoverInfoProps>()

const binaryLabel = (binary: boolean | null): string => {
  if (binary === true) return "Semi-naturel"
  if (binary === false) return "Artificiel"
  return "-"
}

const binaryBadgeClass = (binary: boolean | null): string => {
  if (binary === true) return "bg-primary-100 text-primary-700 border-primary-200"
  if (binary === false) return "bg-orange-100 text-orange-700 border-orange-200"
  return "bg-gray-100 text-gray-600 border-gray-200"
}

const statusDotClass = (binary: boolean | null): string => {
  if (binary === true) return "status-dot--natural"
  if (binary === false) return "status-dot--artificial"
  return "status-dot--neutral"
}
</script>

<template>
  <div v-if="data.landCovers && data.landCovers.length > 0" class="land-cover-list">
    <p class="land-cover-title">Couvertures du sol (rayon 500m)</p>
    <div
      v-for="record in props.data.landCovers"
      :key="record.landCover"
      class="land-cover-row"
      role="listitem"
    >
      <span :class="['status-dot', statusDotClass(record.binary)]" />
      <span class="land-cover-label">{{ record.landCoverLabel }}</span>
      <div class="land-cover-values">
        <span class="land-cover-percentage">{{ record.percentage }}%</span>
        <span :class="['land-cover-badge', binaryBadgeClass(record.binary)]">
          {{ binaryLabel(record.binary) }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.land-cover-list {
  @apply flex flex-col gap-3;
}

.land-cover-title {
  @apply text-xs font-medium text-gray-500;
}

.land-cover-row {
  @apply grid items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-3;
  grid-template-columns: 0.5rem minmax(0, 1fr) auto;
}

.status-dot {
  @apply h-2 w-2 rounded-full;
}

.status-dot--natural {
  @apply bg-primary-500;
}

.status-dot--artificial {
  @apply bg-orange-500;
}

.status-dot--neutral {
  @apply bg-gray-300;
}

.land-cover-label {
  @apply min-w-0 text-sm leading-tight text-gray-600;
  overflow-wrap: anywhere;
}

.land-cover-values {
  @apply flex shrink-0 items-center gap-2;
}

.land-cover-percentage {
  @apply text-sm font-semibold text-gray-800;
}

.land-cover-badge {
  @apply inline-flex items-center font-medium rounded-full border;
  @apply px-2 py-0.5 text-xs;
}
</style>
