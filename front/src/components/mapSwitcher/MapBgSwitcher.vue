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
    <map-qpv-toggle-button />
  </div>
</template>
