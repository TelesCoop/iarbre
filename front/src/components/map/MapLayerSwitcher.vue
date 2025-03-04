<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { LayerVisibility, ModelType } from "@/utils/enum"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const mapStore = useMapStore()

const toggleLayer = (modelType: ModelType) => {
  console.log("### 0", modelType)
  mapStore.toggleLayerVisibility(modelType, props.mapId)
}
</script>

<template>
  <div class="map-layer-switcher">
    <h3 class="map-layer-switcher-title">Layers</h3>
    <div class="map-layer-switcher-list">
      <div
        v-for="layer in mapStore.availableLayers"
        :key="layer.modelType"
        class="map-layer-switcher-item"
      >
        <label class="map-layer-switcher-label">
          <input
            type="checkbox"
            :checked="layer.visibility === 'visible'"
            @change="toggleLayer(layer.modelType)"
          />
          <span class="map-layer-switcher-text">{{ layer.title }}</span>
          <span class="map-layer-switcher-color" :style="{ backgroundColor: layer.color }"></span>
        </label>
      </div>
    </div>
  </div>
</template>

<style lang="sass" scoped>
.map-layer-switcher
  z-index: 3
  position: absolute
  top: 1rem
  left: 1rem
  background-color: white
  border-radius: 10px
  box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.3)
  padding: 0.75rem 1.5rem
  min-width: 150px
  font-family: $accent-font

  &-title
    font-size: 1rem
    margin: 0 0 0.5rem 0
    text-align: center

  &-list
    display: flex
    flex-direction: column
    gap: 0.5rem

  &-item
    display: flex
    align-items: center

  &-label
    display: flex
    align-items: center
    cursor: pointer
    gap: 0.5rem

  &-text
    font-size: 0.9rem

  &-color
    width: 12px
    height: 12px
    border-radius: 50%
    display: inline-block
</style>
