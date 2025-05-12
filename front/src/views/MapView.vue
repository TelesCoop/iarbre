<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { ref } from "vue"
import type { MapParams } from "@/types"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_CENTER } from "@/utils/constants"

const router = useRouter()
const route = useRoute()

const mapParams = ref<MapParams>({
  dataType: DataType.PLANTABILITY,
  lng: DEFAULT_MAP_CENTER.lng,
  lat: DEFAULT_MAP_CENTER.lat,
  zoom: 14
})

if (route.name === "mapWithUrlParams") {
  mapParams.value = {
    lng: parseFloat(route.params.lng as string),
    lat: parseFloat(route.params.lat as string),
    zoom: parseFloat(route.params.zoom as string),
    dataType: route.params.dataType as DataType
  }
}
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative hidden sm:block">
    <map-component
      :model-value="mapParams"
      map-id="default"
      @update:model-value="
        (params) => router.replace({ name: 'mapWithUrlParams', params: params as any })
      "
    />
  </div>
  <div class="on-mobile-container">
    <div
      class="bg-white p-4 m-4 rounded-md shadow-lg flex flex-col text-center border-primary-500 border-0.5"
    >
      <span>Le site est indisponible sur mobile.</span>
      <Button class="underline" link severity="secondary"
        >Cliquez ici pour en savoir plus sur IArbre
      </Button>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.map-container {
  height: var(--content-height);
}

.on-mobile-container {
  background-image: url("/images/mobile-screen.png");
  background-repeat: no-repeat;
  background-size: cover;
  height: calc(100vh - var(--header-height) - 1px);
  @apply flex items-center justify-center;
  @apply w-full;
}
</style>
