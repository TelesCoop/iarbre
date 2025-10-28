<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import type { IpaveData } from "@/types/ipave"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import IpaveContextDataInfo from "@/components/contextData/ipave/IpaveContextDataInfo.vue"
import ClickIpaveDivisionData from "../division/ClickIpaveDivisionData.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface IpaveCardProps {
  data?: IpaveData | null
}

const props = withDefaults(defineProps<IpaveCardProps>(), {
  data: null
})
</script>

<template>
  <context-data-main-container
    color-scheme="ipave"
    title="ipave"
    description="Données de végétation de voirie par strate : herbacée, arbustive (< 1.5m) et arborée. "
    :data="props.data"
    empty-message="Cliquez sur un carreau."
    :zoom-level="zoomLevel"
  >
    <template #content="{ data: ipaveData }">
      <ipave-context-data-info :data="ipaveData" />
      <click-ipave-division-data />
    </template>
  </context-data-main-container>
</template>
