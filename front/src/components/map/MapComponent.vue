<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted, type PropType } from "vue"
import { type MapParams } from "@/types/map"

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
  <div class="block lg:flex w-full h-full">
    <map-side-panel />
    <div
      :id="mapId"
      class="map-component relative lg:ml-auto w-screen h-full"
      data-cy="map-component"
    ></div>
  </div>
  <div class="absolute right-0 top-0 lg:hidden mt-2 mr-2">
    <map-config-drawer-toggle />
  </div>
  <div class="legend-container hidden lg:flex">
    <map-legend />
    <map-filters-status />
  </div>
  <div class="lg:hidden flex items-center justify-center">
    <map-context-data-mobile />
  </div>
  <welcome-message />
</template>

<style>
@reference "@/styles/main.css";

.map-component {
  /* Fix weird bug with map by adding margin-left */
  @media (max-width: var(--breakpoint-lg)) {
    width: calc(100vw - var(--width-sidebar));
  }
}

.legend-container {
  @apply absolute flex flex-col items-start pointer-events-none z-30 gap-2 left-105 top-0 mx-1 mt-4;
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
