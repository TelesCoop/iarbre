<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { LayerRenderMode } from "@/types/map"
import { DataType } from "@/utils/enum"

interface RenderModeItemProps {
  dataType: DataType
  mode: LayerRenderMode
  index: number
}

const props = defineProps<RenderModeItemProps>()
const mapStore = useMapStore()

const isActive = () => {
  return (
    mapStore.isLayerActive(props.dataType) &&
    mapStore.getActiveLayerMode(props.dataType) === props.mode
  )
}

const handleClick = () => {
  mapStore.activateLayerWithMode(props.dataType, props.mode)
}
</script>

<template>
  <div
    :class="{
      'bg-primary-50 border-l-4 border-primary-500': isActive()
    }"
    class="p-4 hover:bg-primary-100 transition-colors duration-150 cursor-pointer"
    @click="handleClick"
  >
    <div class="grid grid-cols-12 gap-3 items-center">
      <div class="col-span-2">
        <div
          :class="{
            'from-primary-500 to-primary-600 text-white': isActive(),
            'text-gray-600': !isActive()
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
              'text-primary-700': isActive(),
              'text-gray-800': !isActive()
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
          v-if="isActive()"
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
</template>
