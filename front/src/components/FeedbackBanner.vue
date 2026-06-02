<script lang="ts" setup>
import { ref, computed } from "vue"
import { useRoute } from "vue-router"
import { useAppStore } from "@/stores/app"

const appStore = useAppStore()
const route = useRoute()
const dismissed = ref(false)

const isMapRoute = computed(() => route.name === "map" || route.name === "mapWithUrlParams")

const paddingLeft = computed(() => {
  if (!appStore.isDesktop) return undefined
  if (isMapRoute.value && appStore.sidePanelVisible) {
    return "calc(4.5rem + var(--width-sidepanel))"
  }
  return "4.5rem"
})
</script>

<template>
  <div
    v-if="!dismissed"
    :style="{ paddingLeft }"
    class="flex items-center justify-center gap-4 px-4 py-2 bg-primary-200 text-primary-900 text-sm transition-[padding] duration-300 ease-out"
  >
    <span class="flex-1 text-center">
      Partagez votre avis sur IA·rbre et aidez-nous à améliorer l'outil !
      <button
        class="font-semibold underline underline-offset-2 hover:opacity-70 transition-opacity"
        @click="appStore.feedbackVisible = true"
      >
        Donner mon avis
      </button>
    </span>
    <button
      class="shrink-0 hover:opacity-80 transition-opacity"
      aria-label="Fermer"
      @click="dismissed = true"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          d="M12 4L4 12M4 4L12 12"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
    </button>
  </div>
</template>
