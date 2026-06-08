<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import IconBuilding from "@/components/icons/IconBuilding.vue"
import IconMap from "@/components/icons/IconMap.vue"
import IconBoundary from "@/components/icons/IconBoundary.vue"

const mapStore = useMapStore()
</script>

<template>
  <div class="layer-toggles">
    <button
      :class="['layer-chip', { active: mapStore.showQPVLayer }]"
      data-cy="qpv-toggle"
      type="button"
      @click="mapStore.toggleQPVLayer()"
    >
      <IconBuilding class="layer-chip__icon" :size="14" />
      QPV
    </button>
    <button
      :class="['layer-chip', { active: mapStore.showCadastreLayer }]"
      data-cy="cadastre-toggle"
      type="button"
      @click="mapStore.toggleCadastreLayer()"
    >
      <IconMap class="layer-chip__icon" :size="14" />
      Cadastre
    </button>
    <button
      :class="['layer-chip', { active: mapStore.showBoundaryLayer }]"
      data-cy="boundary-toggle"
      type="button"
      @click="mapStore.toggleBoundaryLayer()"
    >
      <IconBoundary class="layer-chip__icon" :size="14" />
      Communes
    </button>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.layer-toggles {
  @apply flex items-center gap-1.5 px-2.5 py-1.5;
  @apply bg-white border border-gray-200 rounded-lg;
}

.layer-chip {
  @apply flex items-center gap-1.5 px-3 py-1.5 rounded-full;
  @apply text-xs font-sans font-medium;
  @apply border border-gray-200 bg-white text-gray-700;
  @apply cursor-pointer transition-colors duration-150;
}

/* Green icon gives an inactive chip its identity; it flips to white once active. */
.layer-chip__icon {
  @apply text-primary-500 shrink-0;
}

.layer-chip:hover {
  @apply bg-gray-50 text-gray-900 border-gray-300;
}

.layer-chip.active {
  background-color: var(--color-primary-500);
  border-color: var(--color-primary-500);
  @apply text-white;
}

.layer-chip.active .layer-chip__icon {
  @apply text-white;
}

.layer-chip.active:hover {
  background-color: var(--color-primary-600);
  border-color: var(--color-primary-600);
}
</style>
