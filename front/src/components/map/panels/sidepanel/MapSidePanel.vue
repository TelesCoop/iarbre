<template>
  <div class="hidden md:flex absolute top-0 left-0 z-10 h-full w-100 flex-col bg-white">
    <map-side-panel-header data-cy="map-side-panel-header" class="mb-0" />
    <div class="px-4 flex-1 overflow-y-auto space-y-4 items-center">
      <map-layer-switcher data-cy="map-layer-switcher" />
      <map-context-data data-cy="map-context-data" />
      <map-bg-switcher data-cy="map-bg-switcher" />
      <map-side-panel-download data-cy="map-side-panel-download" />
      <map-side-panel-footer data-cy="map-side-panel-footer" />
    </div>
  </div>
</template>
