<template>
  <!-- Desktop sidepanel -->
  <div :class="['map-sidepanel', { 'is-hidden': !isSidePanelVisible }]" data-cy="map-side-panel">
    <MapSidePanelHeader class="flex-shrink-0" data-cy="map-side-panel-header" />
    <div
      class="px-4 w-full flex-1 min-h-0 flex flex-col overflow-hidden"
      data-cy="map-side-panel-content"
    >
      <MapLayerSwitcher class="w-full" data-cy="map-layer-switcher" />
      <MapContextData class="w-full flex-1 min-h-0 overflow-hidden" data-cy="map-context-data" />
    </div>
    <div class="sidebar-footer" data-cy="map-side-panel-footer">
      <div class="w-full" data-cy="map-side-panel-download">
        <MapSidePanelDownload />
      </div>
    </div>
  </div>

  <!-- Mobile bottom panel -->
  <div :class="{ 'is-open': isPanelOpen }" class="mobile-panel" data-cy="mobile-panel">
    <div class="mobile-panel-header">
      <button class="mobile-panel-handle" data-cy="mobile-panel-handle" @click="togglePanel">
        <span class="handle-text">{{ isPanelOpen ? "Fermer" : "Voir les détails" }}</span>
      </button>
      <div v-if="isPanelOpen" class="mobile-panel-toggles">
        <MapQpvToggleButton />
        <MapCadastreToggleButton />
        <MapBoundaryToggleButton />
        <MapContextTools />
      </div>
    </div>

    <div class="mobile-panel-content">
      <div class="mobile-panel-scroll">
        <MapContextData class="w-full" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import MapBoundaryToggleButton from "../MapBoundaryToggleButton.vue"

const mapStore = useMapStore()
const appStore = useAppStore()

const isSidePanelVisible = computed(() => appStore.sidePanelVisible)
const isPanelOpen = ref(false)

const togglePanel = () => {
  isPanelOpen.value = !isPanelOpen.value
}

// Open panel automatically when context data is set
watch(
  () => mapStore.contextData.data,
  (newData) => {
    if (newData) {
      isPanelOpen.value = true
    }
  }
)
</script>
<style scoped>
@reference "@/styles/main.css";

.map-sidepanel {
  @apply hidden lg:flex h-full flex-col bg-white;
  @apply border-r border-gray-200;
  @apply transition-transform duration-300 ease-out;
  @apply fixed top-0 z-20;
  left: 4.5rem;
  width: var(--width-sidepanel);
}

.map-sidepanel.is-hidden {
  transform: translateX(-100%);
}

.sidebar-footer {
  @apply relative flex items-center;
  @apply bg-primary-500 flex-shrink-0;
  @apply w-full;
  height: 152px;
}

/* Mobile bottom panel */
.mobile-panel {
  @apply lg:hidden fixed left-0 right-0 bg-white z-40;
  @apply rounded-t-2xl;
  @apply transition-transform duration-300 ease-out;
  bottom: 56px;
  transform: translateY(calc(100% - 40px));
}

.mobile-panel.is-open {
  transform: translateY(0);
}

.mobile-panel-header {
  @apply bg-white rounded-t-2xl border-b border-gray-200 flex-shrink-0;
}

.mobile-panel-handle {
  @apply w-full flex items-center justify-center py-3 cursor-pointer;
  @apply min-h-11;
}

.handle-text {
  @apply text-sm font-medium text-gray-700;
}

.mobile-panel-toggles {
  @apply flex items-center justify-center gap-2 px-3 pb-2;
}

.mobile-panel-content {
  @apply flex flex-col;
  max-height: 50vh;
}

.mobile-panel-scroll {
  @apply px-3 pb-3 w-full overflow-y-auto flex-1 min-h-0;
}
</style>
