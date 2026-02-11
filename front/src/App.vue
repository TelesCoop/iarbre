<script setup lang="ts">
import { RouterView, useRoute } from "vue-router"
import { type Component, computed } from "vue"
import { Layout } from "@/utils/constants"
import DefaultLayout from "@/layouts/DefaultLayout.vue"
import { useAppStore } from "@/stores/app"
import { onBeforeUnmount } from "vue"
import AppToast from "@/components/shared/AppToast.vue"

const route = useRoute()
const appStore = useAppStore()

const LAYOUTS: Record<Layout, Component> = {
  [Layout.Default]: DefaultLayout
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
  <AppToast position="bottom-right" group="br" />
  <AppToast position="top-left" group="tl" />
  <AppToast position="top-right" group="tr" />
  <AppToast position="bottom-left" group="bl" />
</template>

<style scoped></style>
