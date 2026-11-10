<script lang="ts" setup>
import { useId } from "vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"
import { useMapStore } from "@/stores/map"
import type { LegendItem } from "@/utils/rasterLayers"

const mapStore = useMapStore()
const uid = useId()

const isVisible = (key: string) => !mapStore.hiddenToggles.includes(key)

const swatchStyle = (item: LegendItem) => ({
  backgroundColor: item.color,
  border: item.border
    ? `2px ${item.border.dashed ? "dashed" : "solid"} ${item.border.color}`
    : "none"
})
</script>

<template>
  <div class="flex flex-col gap-2 py-2">
    <section
      v-for="card in mapStore.selectedLayer.cards"
      :key="card.key"
      class="flex flex-col gap-1.5 bg-white border border-gray-200 rounded-lg p-2.5"
      :data-cy="`legend-card-${card.key}`"
    >
      <div class="flex items-center gap-2">
        <AppToggleSwitch
          :id="`${uid}-${card.key}`"
          size="sm"
          :model-value="isVisible(card.key)"
          :data-cy="`legend-toggle-${card.key}`"
          @update:model-value="mapStore.toggleLayerGroup(card)"
        />
        <label :for="`${uid}-${card.key}`" class="text-sm font-bold text-gray-800 cursor-pointer">
          {{ card.label }}
        </label>
      </div>
      <p class="text-xs text-gray-600">{{ card.description }}</p>

      <div v-if="card.legendStyle === 'swatch'" class="flex flex-col gap-1">
        <div v-for="item in card.legend" :key="item.label" class="flex items-center gap-2">
          <span class="w-8 h-4 shrink-0 rounded" :style="swatchStyle(item)"></span>
          <span class="text-xs text-gray-700">{{ item.label }}</span>
        </div>
      </div>
      <div v-else class="grid grid-cols-3 gap-1.5">
        <div
          v-for="item in card.legend"
          :key="item.label"
          class="flex flex-col items-center justify-center text-center rounded-md px-1 py-1 text-gray-900"
          :class="card.legendStyle === 'outline' ? 'bg-white border-2' : ''"
          :style="
            card.legendStyle === 'outline'
              ? { borderColor: item.color }
              : { backgroundColor: item.color }
          "
        >
          <span class="text-sm font-bold leading-tight">{{ item.label }}</span>
          <span class="text-xs leading-tight">{{ item.detail }}</span>
        </div>
      </div>

      <div v-for="toggle in card.subToggles" :key="toggle.key" class="flex items-center gap-2">
        <AppToggleSwitch
          :id="`${uid}-${toggle.key}`"
          size="sm"
          :model-value="isVisible(toggle.key)"
          :data-cy="`legend-toggle-${toggle.key}`"
          @update:model-value="mapStore.toggleLayerGroup(toggle)"
        />
        <label :for="`${uid}-${toggle.key}`" class="text-xs text-gray-700 cursor-pointer">
          {{ toggle.label }}
        </label>
      </div>
    </section>
    <p class="text-xs text-gray-500">Source : {{ mapStore.selectedLayer.attribution }}</p>
  </div>
</template>
