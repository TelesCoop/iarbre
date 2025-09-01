<template>
  <div class="hidden md:flex absolute top-0 left-0 z-10 h-full w-100 flex-col bg-white">
    <map-side-panel-header />
    <div class="mx-5 flex-1 overflow-y-auto space-y-3 items-center py-4">
      <map-bg-switcher />
      <map-layer-switcher />
      <map-context-data
        class="max-h-[calc(100vh-6rem)] sm:max-h-[calc(100vh-7rem)] lg:max-h-[calc(100vh-6rem)] py-4!"
      />
      <map-side-panel-footer />
    </div>
  </div>
</template>
