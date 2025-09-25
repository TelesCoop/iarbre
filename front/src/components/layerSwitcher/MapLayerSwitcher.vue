<script lang="ts" setup>
interface Props {
  withBorder?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true
})
</script>

<template>
  <div :class="{ 'map-tool-container': props.withBorder }" data-cy="map-layer-switcher">
    <layer-switcher />
    <map-context-tools />
  </div>
</template>
