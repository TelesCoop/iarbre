<script lang="ts" setup>
export interface MapFeatureInfoRow {
  label: string
  value: string
}

defineProps<{
  title: string
  rows: MapFeatureInfoRow[]
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <div class="map-control-panel">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <slot name="icon" />
        <span class="text-sm font-medium font-sans">{{ title }}</span>
      </div>
      <MapControlButton
        aria-label="Fermer"
        class="w-7 h-7 text-gray-400 hover:text-gray-600 hover:bg-gray-100 hover:border-gray-200"
        size="sm"
        @click="emit('close')"
      >
        <IconClose :size="12" />
      </MapControlButton>
    </div>
    <div class="flex flex-col gap-1 mt-2 pt-2 border-t border-gray-100">
      <div v-for="row in rows" :key="row.label" class="flex items-center justify-between gap-4">
        <span class="text-xs font-sans text-gray-500">{{ row.label }}</span>
        <span class="text-xs font-sans font-medium text-gray-800 text-right">{{ row.value }}</span>
      </div>
    </div>
  </div>
</template>
