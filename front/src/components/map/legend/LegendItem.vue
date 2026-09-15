<script lang="ts" setup>
defineProps<{
  label: string
  color: string
}>()
</script>

<template>
  <span class="strate-swatch" :style="{ backgroundColor: color }"></span>
  <span class="strate-label">{{ label }}</span>
</template>
