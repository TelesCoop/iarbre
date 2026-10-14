<script lang="ts" setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import FeedbackBanner from "@/components/FeedbackBanner.vue"

const route = useRoute()
const isMapRoute = computed(() => route.name === "map" || route.name === "mapWithUrlParams")
</script>

<template>
  <div :class="['flex flex-col', isMapRoute ? 'viewport-height' : 'min-h-screen']">
    <FeedbackBanner />
    <main :class="['flex-1', { 'min-h-0': isMapRoute }]">
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.viewport-height {
  height: 100vh;
  height: 100dvh;
}
</style>
