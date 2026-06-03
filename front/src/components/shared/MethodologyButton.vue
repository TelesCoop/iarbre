<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataTypeToDocumentationUrl } from "@/utils/enum"
import AppButton from "@/components/shared/AppButton.vue"
import IconInfo from "@/components/icons/IconInfo.vue"

const mapStore = useMapStore()

const documentationUrl = computed(() => DataTypeToDocumentationUrl[mapStore.selectedDataType])

const openMethodology = () => {
  window.open(documentationUrl.value, "_blank", "noopener,noreferrer")
}
</script>

<template>
  <AppButton
    class="methodology-button"
    data-cy="methodology-button"
    size="sm"
    title="Documentation sur la méthodologie - nouvelle fenêtre"
    variant="gold"
    @click="openMethodology"
  >
    <template #icon-left>
      <IconInfo :size="14" aria-hidden="true" />
    </template>
    <span class="sm:hidden">Méthodologie</span>
    <span class="hidden sm:inline">Voir la méthodologie</span>
  </AppButton>
</template>

<style scoped>
@reference "@/styles/main.css";

.methodology-button {
  @apply px-2.5 py-1 text-xs gap-1 whitespace-nowrap;
}
</style>
