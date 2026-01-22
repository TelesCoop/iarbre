<template>
  <div class="map-sidepanel" data-cy="map-side-panel">
    <map-side-panel-header class="mb-0" data-cy="map-side-panel-header" />
    <div class="flex-1 items-center flex flex-col overflow-hidden">
      <div class="px-4 w-full overflow-y-auto flex-1" data-cy="map-side-panel-content">
        <map-layer-switcher class="w-full" data-cy="map-layer-switcher" />
        <map-context-data class="w-full" data-cy="map-context-data" />
      </div>
      <div class="sidebar-footer">
        <div class="methodology-banner">
          <a
            :href="`https://docs.iarbre.fr/methodology/${mapStore.selectedDataType}/`"
            class="methodology-link"
          >
            <span>Voir la méthodologie</span>
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

        <map-side-panel-download class="w-full" data-cy="map-side-panel-download" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>
<style scoped>
@reference "@/styles/main.css";

.map-sidepanel {
  @apply hidden lg:flex h-full flex-col bg-white w-sidepanel;
  @apply border-r border-gray-200;
  flex-shrink: 0;
}

.methodology-banner {
  @apply px-4 py-3 flex items-center justify-center w-full;
  @apply border-b border-b-gray-200;
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
  @apply bg-primary-500;
  @apply w-full;
  height: 152px;
}
</style>
