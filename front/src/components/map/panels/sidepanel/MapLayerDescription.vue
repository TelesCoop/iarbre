<script lang="ts" setup>
import IconInfo from "@/components/icons/IconInfo.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>

<template>
  <div class="flex flex-col gap-3 px-2 py-4">
    <div
      class="flex flex-col gap-1 bg-white border border-gray-200 rounded-lg p-3"
      data-cy="layer-description"
    >
      <h3 class="text-sm font-bold text-primary-900">{{ mapStore.selectedLayer.label }}</h3>
      <div
        class="flex flex-col gap-2 text-sm text-gray-700 [&_ul]:list-disc [&_ul]:pl-5 [&_a]:text-primary-700 [&_a]:underline"
        v-html="mapStore.selectedLayer.description"
      />
    </div>
    <div class="flex items-start gap-2.5 bg-primary-50 border border-primary-100 rounded-lg p-3">
      <IconInfo class="shrink-0 mt-0.5 text-primary-500" :size="16" aria-hidden="true" />
      <p class="text-sm text-primary-900">
        Sélectionnez un raster ci-dessus pour le visualiser sur la carte. Pour les rasters horaires,
        faites varier l'heure de la journée avec le curseur.
      </p>
    </div>
    <div class="flex items-start gap-2.5 bg-gray-50 border border-gray-100 rounded-lg p-3">
      <IconInfo class="shrink-0 mt-0.5 text-gray-400" :size="16" aria-hidden="true" />
      <p class="text-sm text-gray-700">
        Récupérez les données en cliquant sur
        <span class="font-medium text-gray-900">"Obtenir les données"</span> ou connectez votre QGIS
        à un flux WMS.
      </p>
    </div>
  </div>
</template>
