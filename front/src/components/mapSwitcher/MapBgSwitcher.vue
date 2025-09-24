<script lang="ts" setup>
interface Props {
  withBorder?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true
})
</script>

<template>
  <div :class="{ 'map-bg-tool-container': props.withBorder }" data-cy="map-bg-switcher">
    <span class="font-sans">Fond de carte</span>
    <map-switcher />
    <div class="flex items-center w-full">
      <map-qpv-toggle-button class="flex-1" />
      <map-context-tools class="flex-1" />
    </div>
  </div>
</template>
