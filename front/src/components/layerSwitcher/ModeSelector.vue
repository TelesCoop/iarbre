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

const emit = defineEmits<{
  toggleLayer: [dataType: DataType, mode: LayerRenderMode]
}>()

const handleClick = () => {
  emit("toggleLayer", props.dataType, props.mode)
}
</script>

<template>
  <button
    :class="{
      'bg-primary-500 text-white': isActive(),
      'bg-gray-100 text-gray-700 hover:bg-gray-200': !isActive()
    }"
    class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 cursor-pointer"
    @click="handleClick"
  >
    <span class="text-xs">{{ mapStore.getRenderModeIcon(mode) }}</span>
    <span>{{ mapStore.getRenderModeLabel(mode) }}</span>
  </button>
</template>
