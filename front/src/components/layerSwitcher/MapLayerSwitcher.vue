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
  <div
    :class="['layer-switcher-stack', { 'map-tool-container': props.withBorder }]"
    data-cy="map-layer-switcher"
  >
    <LayerSwitcher />
    <MapContextTools v-if="props.showContextTools" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.layer-switcher-stack {
  @apply flex flex-col gap-2 w-full;
}
</style>
