<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted, type PropType } from "vue"
import { type MapParams } from "@/types"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const model = defineModel<MapParams>({
  required: true,
  type: Object as PropType<MapParams>
})

const emit = defineEmits<{
  "update:modelValue": [value: MapParams]
}>()

const mapStore = useMapStore()

onMounted(() => {
  mapStore.initMap(props.mapId, model.value.dataType!)
  const mapInstance = mapStore.getMapInstance(props.mapId)

  mapInstance.jumpTo({
    center: [model.value.lng, model.value.lat],
    zoom: model.value.zoom
  })

  const updateParams = () => {
    emit("update:modelValue", {
      zoom: Math.round(mapInstance.getZoom()),
      lat: Math.round(100000 * mapInstance.getCenter().lat) / 100000,
      lng: Math.round(100000 * mapInstance.getCenter().lng) / 100000,
      dataType: mapStore.selectedDataType
    })
  }

  mapInstance.on("moveend", updateParams)
  updateParams()
})
</script>

<template>
  <div :id="mapId" class="h-full w-full" data-cy="map-component"></div>
  <map-legend />
  <div class="absolute top-0 left-0 pl-[30px] pt-[30px] flex gap-2 flex-col z-1">
    <map-layer-switcher />
    <map-context-tools />
  </div>
  <div :id="`popup-${mapId}`" :style="{ display: mapStore.popupData ? 'block' : 'none' }">
    <map-score-popup v-if="mapStore.popupData" :popup-data="mapStore.popupData" />
  </div>
</template>
