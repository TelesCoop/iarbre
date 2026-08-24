<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { ref, watch } from "vue"
import type { MapParams } from "@/types/map"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"
import { useMapStore } from "@/stores/map"

const router = useRouter()
const route = useRoute()
const mapStore = useMapStore()

const mapParams = ref<MapParams>({ ...DEFAULT_MAP_PARAMS })
const hasAlreadyChanged = ref<boolean>(false)

if (route.name === "mapWithUrlParams") {
  mapParams.value = {
    lng: parseFloat(route.params.lng as string),
    lat: parseFloat(route.params.lat as string),
    zoom: parseFloat(route.params.zoom as string),
    dataType: route.params.dataType as DataType
  }
}

// Filter values are numeric only for PLANTABILITY, other data types filter on
// string keys (climate zone codes, vegetation strata, biosphere categories, etc.)
const parseFilters = (
  raw: string | string[] | undefined,
  dataType: DataType | null
): (number | string)[] => {
  const rawValue = Array.isArray(raw) ? raw.join(",") : raw
  if (!rawValue) return []
  return rawValue
    .split(",")
    .map((value) => (dataType === DataType.PLANTABILITY ? Number(value) : value))
}

const initialFilters = parseFilters(
  route.query.filters as string | string[] | undefined,
  mapParams.value.dataType
)

// Tracks the last known map position/dataType so filter-only changes can
// rewrite the URL without needing a map move to know the current params.
const lastKnownParams = ref<MapParams>({ ...mapParams.value })

const buildFiltersQuery = () => {
  const values = mapStore.filteredValues
  return values.length > 0 ? { filters: values.map(String).join(",") } : {}
}

const handleMapUpdate = (params: MapParams) => {
  lastKnownParams.value = params

  const replaceUrl = () => {
    router.replace({
      name: "mapWithUrlParams",
      params: {
        ...params,
        lat: params.lat.toFixed(5),
        lng: params.lng.toFixed(5)
      } as any,
      query: buildFiltersQuery()
    })
  }

  if (hasAlreadyChanged.value) {
    replaceUrl()
    return
  }

  const hasChanged = Object.keys(DEFAULT_MAP_PARAMS).some(
    (key) => params[key as keyof MapParams] !== DEFAULT_MAP_PARAMS[key as keyof MapParams]
  )

  if (hasChanged) {
    hasAlreadyChanged.value = true
    replaceUrl()
  }
}

watch(
  () => mapStore.filteredValues,
  () => {
    hasAlreadyChanged.value = true
    router.replace({
      name: "mapWithUrlParams",
      params: {
        ...lastKnownParams.value,
        lat: lastKnownParams.value.lat.toFixed(5),
        lng: lastKnownParams.value.lng.toFixed(5)
      } as any,
      query: buildFiltersQuery()
    })
  },
  { deep: true }
)
</script>

<template>
  <div class="map-view-wrapper">
    <SidebarComponent />
    <MapSidePanel />
    <div class="map-container max-w-screen overflow-hidden relative">
      <MapComponent
        :model-value="mapParams"
        :initial-filters="initialFilters"
        map-id="default"
        @update:model-value="handleMapUpdate"
      />

      <MapScoresDrawer />
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-view-wrapper {
  @apply flex;
  height: calc(100vh - var(--feedback-banner-height, 0px));
  height: calc(100dvh - var(--feedback-banner-height, 0px));
  margin-left: 0;
}

@media (min-width: 1024px) {
  .map-view-wrapper {
    margin-left: 4.5rem;
  }
}

.map-container {
  @apply flex-1;
  height: 100%;
}
</style>
