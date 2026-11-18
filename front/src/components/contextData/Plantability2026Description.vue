<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div
    class="flex flex-col gap-2 mx-2 mt-3 bg-white border border-gray-200 rounded-lg p-3 text-sm text-gray-700"
    data-cy="plantability-2026-description"
  >
    <h3 class="text-sm font-bold text-primary-900">
      {{ DataTypeToLabel[mapStore.selectedDataType] }}
    </h3>
    <p>
      Aperçu de travail du calque de plantabilité 2026, sur Villeurbanne uniquement. Données 2026,
      grille de 5 m (méthode actuelle) ou de 1 m (nouvelle méthode).
    </p>
    <p>Ces cartes servent aux ateliers de validation et vont évoluer.</p>
  </div>
</template>
