<script lang="ts" setup>
import { Drawer, useAppStore } from "@/stores/app"
import { computed } from "vue"
import AppDrawer from "@/components/AppDrawer.vue"

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
    header-icon="pi pi-cog"
    header-title="Carte"
    class="map-config-drawer"
    data-cy="map-config-drawer"
  >
    <map-layer-switcher :with-border="false" />
    <map-bg-switcher :with-border="false" />
    <map-legend />
    <map-context-data />
  </AppDrawer>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-config-drawer > * {
  @apply mb-4;
}
</style>
