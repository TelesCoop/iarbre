<script lang="ts" setup>
import { Sidebar, useAppStore } from "@/stores/app"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const appStore = useAppStore()
const mapStore = useMapStore()

const layerName = computed(
  () => DataTypeToLabel[mapStore.selectedDataType] ?? "Aucune couche sélectionnée"
)
const toggleSidebar = () => {
  appStore.toggleSidebar(Sidebar.MAP_CONFIG)
}
</script>

<template>
  <Button
    @click="toggleSidebar"
    icon="pi pi-cog"
    severity="secondary"
    size="small"
    :aria-label="appStore.sidebarVisible ? 'Close sidebar config' : 'Open sidebar config'"
    data-cy="sidebar-toggle"
    :label="layerName"
  />
</template>

<style scoped></style>
