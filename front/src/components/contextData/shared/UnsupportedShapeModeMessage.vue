<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import AppButton from "@/components/shared/AppButton.vue"

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
      <AppButton size="sm" variant="outline" @click="switchToPointMode">
        <template #icon-left>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
        </template>
        Passer en mode point
      </AppButton>
    </div>
  </div>
</template>
