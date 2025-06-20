<script lang="ts" setup>
import DefaultLayout from "@/layouts/DefaultLayout.vue"
import MapSidebarToggle from "@/components/map/MapSidebarToggle.vue"
import { useAppStore } from "@/stores/app"

const appStore = useAppStore()
</script>

<template>
  <DefaultLayout>
    <template #nav-left v-if="appStore.isMobileOrTablet">
      <div class="nav-left-content">
        <MapSidebarToggle />
      </div>
    </template>

    <slot></slot>
  </DefaultLayout>
</template>

<style scoped>
@reference "@/styles/main.css";

.nav-left-content {
  @apply mr-2;
}
</style>
