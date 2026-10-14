<script lang="ts" setup>
import FilterIndicator from "@/components/map/legend/FilterIndicator.vue"

defineProps<{
  label: string
  color: string
  selected?: boolean
}>()
</script>

<template>
  <span class="strate-swatch relative" :style="{ backgroundColor: color }">
    <FilterIndicator :is-visible="selected ?? false" />
  </span>
  <span class="strate-label">{{ label }}</span>
</template>
