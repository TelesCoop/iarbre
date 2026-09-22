<script lang="ts" setup>
import IconInfo from "@/components/icons/IconInfo.vue"
</script>

<template>
  <div class="flex flex-col gap-3 px-2 py-4">
    <div class="flex items-start gap-2.5 bg-primary-50 border border-primary-100 rounded-lg p-3">
      <IconInfo class="shrink-0 mt-0.5 text-primary-500" :size="16" aria-hidden="true" />
      <p class="text-sm text-primary-900">
        Sélectionnez un raster ci-dessus pour le visualiser sur la carte.
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
