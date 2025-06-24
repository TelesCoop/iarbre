<script lang="ts" setup>
import { Drawer, useAppStore } from "@/stores/app"
import { useMapStore } from "@/stores/map"
import { computed } from "vue"

const props = defineProps<{
  featureId: string | number
}>()
const appStore = useAppStore()
const mapStore = useMapStore()
const buttonLabel = computed(() =>
  appStore.isDesktop && mapStore.contextData.data ? "Masquer les détails" : "Voir les détails"
)
const onClick = () => {
  if (appStore.isDesktop) {
    mapStore.contextData.toggleContextData(props.featureId)
  } else {
    mapStore.contextData.setData(props.featureId)
    appStore.setDrawerVisible(Drawer.MAP_SCORES, true)
  }
}
</script>

<template>
  <Button
    :label="buttonLabel"
    class="font-accent"
    severity="secondary"
    size="small"
    @click="onClick"
  />
</template>
