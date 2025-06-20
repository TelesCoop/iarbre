<script lang="ts" setup>
import { useAppStore } from "@/stores/app"

const appStore = useAppStore()

const toggleSidebar = () => {
  appStore.toggleSidebar()
}
</script>

<template>
  <Button
    @click="toggleSidebar"
    icon="pi pi-bars"
    severity="secondary"
    size="small"
    :aria-label="appStore.sidebarVisible ? 'Close sidebar' : 'Open sidebar'"
    data-cy="sidebar-toggle"
  />
</template>

<style scoped></style>
