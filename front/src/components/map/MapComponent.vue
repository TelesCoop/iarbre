<script lang="ts" setup>
import { useMapStore } from '@/stores/map'
import { onMounted } from 'vue'

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const mapStore = useMapStore()
const mapInstance = mapStore.getMapInstance(props.mapId)

onMounted(() => {
  mapStore.initMap(props.mapId)
  console.log('initMap', props.mapId)
  // setTimeout(() => {
  //   mapInstance.value.resize()
  // }, 100)
  // mapInstance.on('load', () => {
  //   map.resize()
  // })
})
</script>

<template>
  <div :id="mapId" height="100%"></div>
</template>
