<script lang="ts" setup>
import MethodologyButton from "@/components/shared/MethodologyButton.vue"

interface Props {
  withBorder?: boolean
  showContextTools?: boolean
  showMethodology?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true,
  showContextTools: true,
  showMethodology: true
})
</script>

<template>
  <div
    :class="['layer-switcher-stack', { 'map-tool-container': props.withBorder }]"
    data-cy="map-layer-switcher"
  >
    <LayerSwitcher />
    <MethodologyButton v-if="props.showMethodology" class="self-end" />
    <MapContextTools v-if="props.showContextTools" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.layer-switcher-stack {
  @apply flex flex-col gap-2 w-full;
}
</style>
