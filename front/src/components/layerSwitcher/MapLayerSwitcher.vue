<script lang="ts" setup>
interface Props {
  withBorder?: boolean
  showContextTools?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true,
  showContextTools: true
})
</script>

<template>
  <div :class="{ 'map-tool-container': props.withBorder }" data-cy="map-layer-switcher">
    <LayerSwitcher />
    <MapContextTools v-if="props.showContextTools" />
  </div>
</template>
