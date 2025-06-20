<script setup lang="ts">
import { RouterView, useRoute } from "vue-router"
import { type Component, computed } from "vue"
import { Layout } from "@/utils/constants"
import DefaultLayout from "@/layouts/DefaultLayout.vue"
import { useAppStore } from "@/stores/app"
import { onBeforeUnmount } from "vue"
import MapLayout from "./layouts/MapLayout.vue"

const route = useRoute()
const appStore = useAppStore()

const LAYOUTS: Record<Layout, Component> = {
  [Layout.Default]: DefaultLayout,
  [Layout.Map]: MapLayout
}
const layout = computed(() => {
  const layoutName = (route.meta.layout || Layout.Default) as Layout
  return LAYOUTS[layoutName]
})

appStore.mountDetectResize()

onBeforeUnmount(() => {
  appStore.unmountDetectResize()
})
</script>

<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>

<style scoped></style>
