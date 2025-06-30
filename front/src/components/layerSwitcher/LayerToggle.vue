<script lang="ts" setup>
import { ref } from "vue"
import { useMapStore } from "@/stores/map"
import ModeSelector from "./ModeSelector.vue"
import type { DataLayerMetadata } from "@/composables/useDataLayerMetadata"
import { DataType } from "@/utils/enum"
import { LayerRenderMode } from "@/types/map"

interface LayerToggleProps {
  layerMetadata: DataLayerMetadata
}

const props = defineProps<LayerToggleProps>()
const mapStore = useMapStore()

const isExpanded = ref(false)

const toggleExpanded = () => {
  const availableModes = getAvailableModes()
  if (availableModes.length === 1) {
    mapStore.toggleLayer(props.layerMetadata.dataType, availableModes[0])
  } else {
    isExpanded.value = !isExpanded.value
  }
}

const isLayerActive = () => {
  return mapStore.isLayerActive(props.layerMetadata.dataType)
}

const getActiveMode = () => {
  return mapStore.getActiveLayerMode(props.layerMetadata.dataType)
}

const getAvailableModes = () => {
  return mapStore.getAvailableRenderModes(props.layerMetadata.dataType)
}

const handleLayerToggle = (dataType: DataType, mode: LayerRenderMode) => {
  mapStore.toggleLayer(dataType, mode)
}
</script>

<template>
  <div class="overflow-hidden">
    <button
      :class="{
        'bg-primary-50 border-l-4 border-primary-500': isLayerActive()
      }"
      class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex items-center justify-between text-left"
      @click="toggleExpanded"
    >
      <div class="flex items-center gap-3">
        <span class="text-lg">{{ layerMetadata.icon }}</span>
        <div>
          <h3 class="font-medium text-gray-900 text-sm">{{ layerMetadata.label }}</h3>
          <p class="text-xs text-gray-600 mt-0.5">
            {{ layerMetadata.description }}
            <span v-if="isLayerActive()" class="ml-1 text-primary-600 font-medium">
              • {{ mapStore.getRenderModeLabel(getActiveMode()!) }}
            </span>
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <svg
          v-if="getAvailableModes().length > 1"
          :class="[
            'w-5 h-5 text-gray-400 transition-transform duration-200',
            isExpanded ? 'transform rotate-180' : ''
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            d="M19 9l-7 7-7-7"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
        </svg>
        <div
          v-if="isLayerActive()"
          class="w-3 h-3 bg-primary-500 rounded-full flex items-center justify-center"
        >
          <svg class="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path
              clip-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              fill-rule="evenodd"
            />
          </svg>
        </div>
      </div>
    </button>

    <div v-if="isExpanded" class="p-3 bg-gray-50 flex flex-wrap gap-2">
      <ModeSelector
        v-for="(mode, index) in getAvailableModes()"
        :key="mode"
        :data-type="layerMetadata.dataType"
        :index="index"
        :mode="mode"
        @toggle-layer="handleLayerToggle"
      />
    </div>
  </div>
</template>
