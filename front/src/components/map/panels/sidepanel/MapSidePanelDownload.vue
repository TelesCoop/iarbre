<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"
import { DataTypeToDownloadLink } from "@/utils/enum"

const mapStore = useMapStore()
const selectedDataType = computed(() => mapStore.selectedDataType)
const downloadLink = computed(() => DataTypeToDownloadLink[selectedDataType.value])

const handleDownload = () => {
  window.open(downloadLink.value, "_blank")
}
</script>

<template>
  <div
    class="flex bg-primary-500 w-full font-sans text-white text-base text-center py-4 rounded-md border border-primary-900"
  >
    <div class="w-full flex flex-col items-center gap-4">
      <span>🌱 Collectivités, aménageurs, urbanistes</span>
      <span class="text-xs">Demandez les données pour ce calque</span>
      <button
        class="cursor-pointer bg-white font-sans flex items-center px-[1.44rem] py-[0.62rem] rounded-3xl text-sm text-primary-500"
        data-cy="download-data"
        @click="handleDownload"
      >
        Obtenir les données
        <svg
          class="ml-2"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M11.5 5.5L14 8M14 8L11.5 10.5M14 8H2"
            stroke="#426A45"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </div>
</template>
