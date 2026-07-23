<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

defineProps<{
  value: number | string
  label: string
}>()

const mapStore = useMapStore()
</script>

<template>
  <button
    type="button"
    :aria-label="`${label} — cliquez pour filtrer`"
    :aria-pressed="mapStore.isFiltered(value)"
    :class="[
      mapStore.isFiltered(value) ? 'is-selected' : '',
      mapStore.hasActiveFilters && !mapStore.isFiltered(value) ? 'is-dimmed' : ''
    ]"
    @click="mapStore.toggleAndApplyFilter(value)"
  >
    <slot />
  </button>
</template>
