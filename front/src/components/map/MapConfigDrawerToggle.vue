<script lang="ts" setup>
import { Drawer, useAppStore } from "@/stores/app"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const appStore = useAppStore()
const mapStore = useMapStore()

const layerName = computed(
  () => DataTypeToLabel[mapStore.selectedDataType] ?? "Aucune couche sélectionnée"
)
const toggleDrawer = () => {
  appStore.toggleDrawer(Drawer.MAP_CONFIG)
}
</script>

<template>
  <Button
    icon="pi pi-cog"
    severity="secondary"
    size="small"
    :aria-label="appStore.drawerVisible ? 'Close drawer config' : 'Open drawer config'"
    data-cy="drawer-toggle"
    :label="layerName"
    @click="toggleDrawer"
  />
</template>

<style scoped></style>
