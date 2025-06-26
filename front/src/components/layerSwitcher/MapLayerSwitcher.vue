<script lang="ts" setup>
import DataLayerSection from "./DataLayerSection.vue"
import { useDataLayerMetadata } from "@/composables/useDataLayerMetadata"

const { dataLayerOptions } = useDataLayerMetadata()
</script>

<template>
  <div
    class="max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto scrollbar border border-gray-200 rounded-lg"
  >
    <DataLayerSection
      v-for="layerMetadata in dataLayerOptions"
      :key="layerMetadata.dataType"
      :layer-metadata="layerMetadata"
    />
  </div>
</template>
