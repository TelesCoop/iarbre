<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import Button from "primevue/button"

const mapStore = useMapStore()

const switchToPointMode = () => {
  mapStore.changeSelectionMode(SelectionMode.POINT)
}
</script>

<template>
  <div v-if="mapStore.isShapeMode" class="flex items-center justify-center pb-6 text-center">
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p class="text-brown font-semibold mb-2">Score non disponible</p>
      <p class="text-sm text-gray-600 mb-3">
        Le score des zones climatiques n'est pas supporté pour les sélections de type polygone,
        rectangle ou cercle. Utilisez le mode de sélection par point.
      </p>
      <Button size="small" severity="secondary" outlined @click="switchToPointMode">
        <i class="pi pi-map-marker mr-2"></i>
        Passer en mode point
      </Button>
    </div>
  </div>
</template>
