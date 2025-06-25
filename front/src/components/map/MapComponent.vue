<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted, type PropType } from "vue"
import { type MapParams } from "@/types/map"
import { Drawer, useAppStore } from "@/stores/app"

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

const appStore = useAppStore()
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
      zoom: Math.round(mapStore.currentZoom),
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
  <div class="absolute right-0 top-0 lg:hidden mt-2 mr-2">
    <map-config-drawer-toggle />
  </div>
  <div class="legend-container hidden lg:flex">
    <map-legend />
    <div class="flex gap-2">
      <map-filters-status />
      <map-context-tools class="ml-auto" />
    </div>
  </div>
  <div
    class="absolute hidden lg:flex top-0 left-0 ml-1 sm:ml-2 lg:ml-8 mt-4 mr-1 sm:mr-2 gap-2 flex-col z-1 w-[20rem] md:w-[24rem] lg:w-[26rem] xl:w-[30rem] 2xl:w-[32rem] max-w-[calc(100vw-0.5rem)]"
  >
    <map-layer-switcher />
    <map-bg-switcher />
    <map-context-data
      class="max-h-[calc(100vh-6rem)] sm:max-h-[calc(100vh-7rem)] lg:max-h-[calc(100vh-6rem)] p-0!"
    />
  </div>
  <div :id="`popup-${mapId}`" :style="{ display: mapStore.popupData ? 'block' : 'none' }">
    <map-score-popup />
  </div>
</template>

<style>
@reference "@/styles/main.css";

.legend-container {
  position: absolute;
  margin-top: 1rem;
  z-index: 30;
  flex-direction: column;
  align-items: flex-end;
  pointer-events: none;
  @apply gap-2;
  @apply top-0 right-0;
  @apply mx-1;
}

.legend-container > * {
  pointer-events: auto;
  flex: 1;
  width: 100%;
}

@media (min-width: 1024px) {
  .legend-container {
    margin-right: 2rem;
  }
}

.maplibregl-ctrl-geocoder {
  width: 90%;
  max-width: 400px;
}

.maplibregl-ctrl-geocoder--suggestions {
  width: 100%;
}
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed,
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed .maplibregl-ctrl-geocoder--input {
  width: 30px;
  min-width: 30px;
  height: 30px;
}
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed .maplibregl-ctrl-geocoder--icon {
  width: 25px;
  height: 25px;
  top: 3px;
  left: 3px;
}

.maplibregl-ctrl-geocoder--input {
  @apply text-primary-500;
  @apply font-accent;
}

.maplibregl-ctrl-geocoder--icon-search {
  @apply fill-primary-500;
}
</style>
