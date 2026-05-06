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
  if (binary === true) return "bg-green-100 text-green-700"
  if (binary === false) return "bg-orange-100 text-orange-700"
  return "bg-gray-100 text-gray-600"
}

const rowBgClass = (binary: boolean | null): string => {
  if (binary === true) return "bg-green-50 border-green-200"
  if (binary === false) return "bg-orange-50 border-orange-200"
  return "bg-gray-50 border-gray-200"
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
      :class="[
        'flex items-center justify-between gap-2 py-2 px-2.5 border rounded-md',
        rowBgClass(record.binary)
      ]"
      role="listitem"
    >
      <span class="text-sm font-medium text-gray-800 leading-tight">{{
        record.landCoverLabel
      }}</span>
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-sm font-bold text-gray-700">{{ record.percentage }}%</span>
        <span
          :class="[
            'text-xs font-semibold px-2 py-0.5 rounded-full',
            binaryBadgeClass(record.binary)
          ]"
        >
          {{ binaryLabel(record.binary) }}
        </span>
      </div>
    </div>
  </div>
</template>
