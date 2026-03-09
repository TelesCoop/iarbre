<template>
  <!-- Desktop sidepanel -->
  <div :class="['map-sidepanel', { 'is-hidden': !isSidePanelVisible }]" data-cy="map-side-panel">
    <MapSidePanelHeader class="flex-shrink-0" data-cy="map-side-panel-header" />
    <div
      class="px-4 w-full flex-1 min-h-0 flex flex-col overflow-hidden"
      data-cy="map-side-panel-content"
    >
      <MapLayerSwitcher class="w-full" data-cy="map-layer-switcher" />
      <div class="flex flex-wrap items-center justify-center gap-2 py-2">
        <MapQpvToggleButton />
        <MapCadastreToggleButton />
      </div>
      <MapContextData class="w-full flex-1 min-h-0 overflow-hidden" data-cy="map-context-data" />
    </div>
    <div class="sidebar-footer" data-cy="map-side-panel-footer">
      <div class="methodology-banner">
        <a
          :href="`https://docs.iarbre.fr/methodology/${mapStore.selectedDataType}/`"
          class="methodology-link"
        >
          <span class="underline">Voir la méthodologie</span>
          <svg
            fill="none"
            height="16"
            viewBox="0 0 16 16"
            width="16"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M6 12L10 8L6 4"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
          </svg>
        </a>
      </div>

      <MapSidePanelDownload class="w-full" data-cy="map-side-panel-download" />
    </div>
  </div>

  <!-- Mobile bottom panel -->
  <div :class="{ 'is-open': isPanelOpen }" class="mobile-panel" data-cy="mobile-panel">
    <div class="mobile-panel-header">
      <button class="mobile-panel-handle" data-cy="mobile-panel-handle" @click="togglePanel">
        <div class="handle-bar"></div>
        <div class="handle-row">
          <span class="handle-text">{{ isPanelOpen ? "Fermer" : "Voir les détails" }}</span>
          <svg
            :class="{ 'rotate-180': isPanelOpen }"
            class="handle-icon"
            fill="none"
            height="14"
            viewBox="0 0 16 16"
            width="14"
          >
            <path
              d="M4 10L8 6L12 10"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
          </svg>
        </div>
      </button>
      <div v-if="isPanelOpen" class="mobile-panel-toggles">
        <MapQpvToggleButton />
        <MapCadastreToggleButton />
        <MapContextTools />
      </div>
    </div>

    <div class="mobile-panel-content">
      <div class="mobile-panel-scroll">
        <MapContextData class="w-full" />
        <a
          :href="`https://docs.iarbre.fr/methodology/${mapStore.selectedDataType}/`"
          class="methodology-link-mobile"
        >
          Voir la méthodologie
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"

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
  left: 64px;
  width: var(--width-sidepanel);
}

.map-sidepanel.is-hidden {
  transform: translateX(-100%);
}

.methodology-banner {
  @apply px-4 py-3 flex items-center justify-center w-full;
  @apply border-b border-b-primary-300;
  flex-shrink: 0;
}

.methodology-link {
  @apply flex items-center gap-2 text-off-white text-sm font-sans font-medium;
  @apply hover:underline cursor-pointer;
  text-decoration: none;
  transition: opacity 0.2s;
}

.methodology-link:hover {
  opacity: 0.9;
}

.sidebar-footer {
  @apply relative;
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
  @apply w-full flex flex-col items-center py-1.5 cursor-pointer;
}

.handle-bar {
  @apply w-10 h-1 bg-gray-300 rounded-full;
}

.handle-row {
  @apply flex items-center gap-1 py-2;
}

.handle-text {
  @apply text-xs font-medium text-gray-500;
}

.handle-icon {
  @apply text-gray-400 transition-transform duration-300;
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

.methodology-link-mobile {
  @apply text-primary-500 text-xs font-medium text-center block pt-3 mt-2;
  @apply border-t border-gray-100;
  text-decoration: underline;
}
</style>
