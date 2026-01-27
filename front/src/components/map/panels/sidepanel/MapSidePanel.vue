<template>
  <!-- Remove this block with v-if for tutorial to avoid select this element instead of mobile element -->
  <div
    class="absolute top-0 left-0 z-10 h-full flex-col bg-white w-sidepanel"
    data-cy="map-side-panel"
  >
    <map-side-panel-header data-cy="map-side-panel-header" class="mb-0" />
    <div class="px-4 flex-1 overflow-y-auto items-center">
      <map-layer-switcher data-cy="map-layer-switcher" class="mb-4" />
      <map-context-data data-cy="map-context-data" />
      <map-bg-switcher data-cy="map-bg-switcher" class="mb-4" />
      <map-side-panel-download data-cy="map-side-panel-download" class="mb-4" />
      <map-side-panel-footer data-cy="map-side-panel-footer" />
    </div>
  </div>
</template>
