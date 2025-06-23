<script lang="ts" setup>
import { Sidebar, useAppStore } from "@/stores/app"
import { computed } from "vue"
import AppSidebar from "@/components/AppSidebar.vue"

const appStore = useAppStore()

const sidebarVisible = computed({
  get: () => appStore.isMobileOrTablet && appStore.sidebarVisible[Sidebar.MAP_CONFIG],
  set: (value: boolean) => appStore.setSidebarVisible(Sidebar.MAP_CONFIG, value)
})
</script>

<template>
  <AppSidebar
    v-model:visible="sidebarVisible"
    position="left"
    header-icon="pi pi-cog"
    header-title="Carte"
    class="map-config-sidebar"
  >
    <map-layer-switcher />
    <map-bg-switcher />
    <map-legend />
    <map-filters-status />
  </AppSidebar>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-config-sidebar > * {
  @apply mb-4;
}
</style>
