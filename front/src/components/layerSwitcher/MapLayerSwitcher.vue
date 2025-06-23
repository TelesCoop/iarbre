<script lang="ts" setup>
import { ref } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()

const dataTypeOptions = [
  {
    dataType: DataType.PLANTABILITY,
    label: DataTypeToLabel[DataType.PLANTABILITY],
    icon: "🌱",
    description: "Potentiel de plantation d'arbres"
  },
  {
    dataType: DataType.VULNERABILITY,
    label: DataTypeToLabel[DataType.VULNERABILITY],
    icon: "🌡️",
    description: "Vulnérabilité climatique"
  },
  {
    dataType: DataType.CLIMATE_ZONE,
    label: DataTypeToLabel[DataType.CLIMATE_ZONE],
    icon: "🌍",
    description: "Zones climatiques locales"
  }
]

const expandedLayers = ref<Record<DataType, boolean>>({
  [DataType.PLANTABILITY]: false,
  [DataType.VULNERABILITY]: false,
  [DataType.CLIMATE_ZONE]: false
})

const toggleLayer = (dataType: DataType) => {
  expandedLayers.value[dataType] = !expandedLayers.value[dataType]
}
</script>

<template>
  <div
    class="max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto scrollbar border border-gray-200 rounded-lg"
  >
    <div v-for="option in dataTypeOptions" :key="option.dataType" class="overflow-hidden">
      <button
        :class="{
          'bg-primary-50 border-l-4 border-primary-500': mapStore.isLayerActive(option.dataType)
        }"
        class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex items-center justify-between text-left"
        @click="toggleLayer(option.dataType)"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">{{ option.icon }}</span>
          <div>
            <h3 class="font-medium text-gray-900 text-sm">{{ option.label }}</h3>
            <p class="text-xs text-gray-600 mt-0.5">
              {{ option.description }}
              <span
                v-if="mapStore.isLayerActive(option.dataType)"
                class="ml-1 text-primary-600 font-medium"
              >
                • {{ mapStore.getRenderModeLabel(mapStore.getActiveLayerMode(option.dataType)!) }}
              </span>
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div
            v-if="mapStore.isLayerActive(option.dataType)"
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
          <svg
            :class="[
              'w-5 h-5 text-gray-400 transition-transform duration-200',
              expandedLayers[option.dataType] ? 'transform rotate-180' : ''
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
        </div>
      </button>

      <div v-if="expandedLayers[option.dataType]" class="divide-y divide-gray-100 bg-white">
        <div
          v-for="(mode, index) in mapStore.getAvailableRenderModes(option.dataType)"
          :key="mode"
          :class="{
            'bg-primary-50 border-l-4 border-primary-500':
              mapStore.isLayerActive(option.dataType) &&
              mapStore.getActiveLayerMode(option.dataType) === mode
          }"
          class="p-4 hover:bg-primary-100 transition-colors duration-150 cursor-pointer"
          @click="mapStore.activateLayerWithMode(option.dataType, mode)"
        >
          <div class="grid grid-cols-12 gap-3 items-center">
            <div class="col-span-2">
              <div
                :class="{
                  'from-primary-500 to-primary-600 text-white':
                    mapStore.isLayerActive(option.dataType) &&
                    mapStore.getActiveLayerMode(option.dataType) === mode,
                  'text-gray-600': !(
                    mapStore.isLayerActive(option.dataType) &&
                    mapStore.getActiveLayerMode(option.dataType) === mode
                  )
                }"
                class="w-6 h-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center text-xs"
              >
                {{ mapStore.getRenderModeIcon(mode) }}
              </div>
            </div>
            <div class="col-span-8">
              <div class="flex flex-col">
                <span
                  :class="{
                    'text-primary-700':
                      mapStore.isLayerActive(option.dataType) &&
                      mapStore.getActiveLayerMode(option.dataType) === mode,
                    'text-gray-800': !(
                      mapStore.isLayerActive(option.dataType) &&
                      mapStore.getActiveLayerMode(option.dataType) === mode
                    )
                  }"
                  class="font-medium text-sm leading-tight"
                >
                  {{ mapStore.getRenderModeLabel(mode) }}
                </span>
                <span class="text-xs text-gray-500 mt-1"> Mode {{ index + 1 }} • {{ mode }} </span>
              </div>
            </div>
            <div class="col-span-2 flex justify-end">
              <div
                v-if="
                  mapStore.isLayerActive(option.dataType) &&
                  mapStore.getActiveLayerMode(option.dataType) === mode
                "
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
