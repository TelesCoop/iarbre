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
    <div class="flex-1 hidden lg:flex">
      <layer-switcher-icon color="426A45" />
    </div>
  </div>
</template>
