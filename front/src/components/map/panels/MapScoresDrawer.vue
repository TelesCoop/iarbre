<script lang="ts" setup>
import { Drawer, useAppStore } from "@/stores/app"
import { computed } from "vue"
import AppDrawer from "@/components/AppDrawer.vue"

const appStore = useAppStore()

const drawerVisible = computed({
  get: () => appStore.isMobileOrTablet && appStore.drawerVisible[Drawer.MAP_SCORES],
  set: (value: boolean) => appStore.setDrawerVisible(Drawer.MAP_SCORES, value)
})
</script>

<template>
  <AppDrawer
    v-model:visible="drawerVisible"
    position="bottom"
    header-icon="pi pi-map"
    header-title="Score"
    class="map-drawer"
    data-cy="map-drawer"
  >
    <div class="mb-4">
      <map-context-data hide-close-button full-height />
    </div>
  </AppDrawer>
</template>

<style scoped></style>
