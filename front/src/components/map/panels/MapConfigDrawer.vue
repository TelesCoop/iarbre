<script lang="ts" setup>
import { Drawer, useAppStore } from "@/stores/app"
import { computed } from "vue"
import AppDrawer from "@/components/AppDrawer.vue"
import IconSettings from "@/components/icons/IconSettings.vue"

const appStore = useAppStore()

const drawerVisible = computed({
  get: () => appStore.isMobileOrTablet && appStore.drawerVisible[Drawer.MAP_CONFIG],
  set: (value: boolean) => appStore.setDrawerVisible(Drawer.MAP_CONFIG, value)
})
</script>

<template>
  <AppDrawer
    v-model:visible="drawerVisible"
    position="bottom"
    header-title="Carte"
    class="map-config-drawer"
    data-cy="map-config-drawer"
  >
    <template #icon>
      <IconSettings :size="20" />
    </template>
    <MapLayerSwitcher :with-border="false" />
    <MapBgSwitcher :with-border="false" />
    <MapLegend />
    <MapFiltersStatus />
    <MapContextData />
  </AppDrawer>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-config-drawer > * {
  @apply mb-4;
}
</style>
