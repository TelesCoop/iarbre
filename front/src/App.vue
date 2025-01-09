<script setup lang="ts">
import { RouterView, useRoute } from "vue-router"
import { type Component, computed } from "vue"
import { Layout } from "@/utils/constants"
import DefaultLayout from "@/layouts/DefaultLayout.vue"

const route = useRoute()

const LAYOUTS: Record<Layout, Component> = {
  [Layout.Default]: DefaultLayout
}
const layout = computed(() => {
  const layoutName = (route.meta.layout || Layout.Default) as Layout
  return LAYOUTS[layoutName]
})
</script>

<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>

<style scoped></style>
