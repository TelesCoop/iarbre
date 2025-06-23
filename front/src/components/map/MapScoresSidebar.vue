<script lang="ts" setup>
import { Sidebar, useAppStore } from "@/stores/app"
import { computed } from "vue"
import AppSidebar from "@/components/AppSidebar.vue"

const appStore = useAppStore()

const sidebarVisible = computed({
  get: () => appStore.isMobileOrTablet && appStore.sidebarVisible[Sidebar.MAP_SCORES],
  set: (value: boolean) => appStore.setSidebarVisible(Sidebar.MAP_SCORES, value)
})
</script>

<template>
  <AppSidebar
    v-model:visible="sidebarVisible"
    position="left"
    header-icon="pi pi-map"
    header-title="Score"
    class="map-sidebar"
  >
    <div class="mb-4">
      <map-context-data hide-close-button />
    </div>
  </AppSidebar>
</template>

<style scoped></style>
