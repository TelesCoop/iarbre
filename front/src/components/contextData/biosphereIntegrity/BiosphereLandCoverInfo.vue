<script lang="ts" setup>
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"

interface BiosphereLandCoverInfoProps {
  data: BiosphereIntegrityData
}

const props = defineProps<BiosphereLandCoverInfoProps>()

const binaryLabel = (binary: boolean | null): string => {
  if (binary === true) return "Semi-naturel"
  if (binary === false) return "Non semi-naturel"
  return "-"
}

const binaryClass = (binary: boolean | null): string => {
  if (binary === true) return "text-green-600"
  if (binary === false) return "text-orange-600"
  return "text-gray-800"
}
</script>

<template>
  <div v-if="data.landCovers && data.landCovers.length > 0" class="flex flex-col gap-1">
    <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">
      Couvertures du sol (rayon 500m)
    </p>
    <div
      v-for="record in props.data.landCovers"
      :key="record.landCover"
      class="flex items-center justify-between gap-2 py-2 px-2.5 bg-gray-50 border border-gray-200 rounded-md"
      role="listitem"
    >
      <span class="text-sm font-medium text-gray-700 leading-tight">{{
        record.landCoverLabel
      }}</span>
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-xs text-gray-500">{{ record.percentage }}%</span>
        <span :class="['text-sm font-semibold', binaryClass(record.binary)]">
          {{ binaryLabel(record.binary) }}
        </span>
      </div>
    </div>
  </div>
</template>
