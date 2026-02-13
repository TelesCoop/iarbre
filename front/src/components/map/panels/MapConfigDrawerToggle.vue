<script lang="ts" setup>
import { computed } from "vue"
import { Drawer, useAppStore } from "@/stores/app"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"
import IconSettings from "@/components/icons/IconSettings.vue"
import AppButton from "@/components/shared/AppButton.vue"

const appStore = useAppStore()
const mapStore = useMapStore()

const isOpen = computed(() => appStore.drawerVisible[Drawer.MAP_CONFIG])

const layerName = computed(
  () => DataTypeToLabel[mapStore.selectedDataType] ?? "Aucune couche sélectionnée"
)

const ariaLabel = computed(() =>
  isOpen.value ? "Fermer le panneau de configuration" : "Ouvrir le panneau de configuration"
)

const handleToggle = () => {
  appStore.toggleDrawer(Drawer.MAP_CONFIG)
}
</script>

<template>
  <AppButton
    :aria-expanded="isOpen"
    :aria-label="ariaLabel"
    data-cy="drawer-toggle"
    size="sm"
    variant="secondary"
    @click="handleToggle"
  >
    <template #icon-left>
      <IconSettings :size="16" aria-hidden="true" />
    </template>
    {{ layerName }}
  </AppButton>
</template>
