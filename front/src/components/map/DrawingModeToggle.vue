<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const isActive = computed(() => mapStore.isToolbarVisible)

const ariaLabel = computed(() =>
  isActive.value ? "Fermer la barre d'outils de dessin" : "Ouvrir la barre d'outils de dessin"
)

const iconSrc = computed(() => `/icons/map-draw${isActive.value ? "-white" : ""}.svg`)

const handleToggle = () => {
  mapStore.toggleToolbar()
}
</script>

<template>
  <MapControlButton
    :active="isActive"
    :aria-label="ariaLabel"
    :aria-pressed="isActive"
    data-cy="drawing-mode-toggle"
    size="sm"
    @click="handleToggle"
  >
    <img :src="iconSrc" alt="" aria-hidden="true" class="w-6 h-6" />
  </MapControlButton>
</template>
