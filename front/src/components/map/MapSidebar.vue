<script lang="ts" setup>
import { useAppStore } from "@/stores/app"
import { useMapStore } from "@/stores/map"
import { computed } from "vue"

const appStore = useAppStore()

const sidebarVisible = computed({
  get: () => appStore.isMobileOrTablet && appStore.sidebarVisible,
  set: (value: boolean) => appStore.setSidebarVisible(value)
})
</script>

<template>
  <Sidebar
    v-model:visible="sidebarVisible"
    position="left"
    class="map-sidebar"
    :style="{ width: '90%', 'max-width': '25rem' }"
  >
    <template #header>
      <div class="flex items-center gap-2">
        <i class="pi pi-map text-xl"></i>
        <span class="font-semibold text-lg">Carte</span>
      </div>
    </template>

    <div class="sidebar-content">
      <div class="mb-4">
        <map-context-data />
      </div>
      <div class="mb-4">
        <map-legend />
      </div>
      <div class="mb-4">
        <map-filters-status />
      </div>
      <div class="mb-4">
        <map-zoom-controls />
      </div>
      <div class="mb-4">
        <map-layer-switcher />
      </div>
      <div class="mb-4">
        <map-bg-switcher />
      </div>
      <div class="mb-4">
        <map-context-tools />
      </div>
    </div>
  </Sidebar>
</template>

<style scoped></style>
