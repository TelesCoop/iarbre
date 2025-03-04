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
        <label class="map-layer-switcher-label" :class="{ 'is-loading': layer.isLoading }">
          <input
            type="checkbox"
            :checked="layer.visibility === 'visible'"
            :disabled="layer.isLoading"
            @change="toggleLayer(layer.modelType)"
          />
          <span class="map-layer-switcher-text">{{ layer.title }}</span>
          <span class="map-layer-switcher-color" :style="{ backgroundColor: layer.color }"></span>
          <span v-if="layer.isLoading" class="map-layer-switcher-loading">
            <span class="loading-spinner"></span>
          </span>
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

  &-loading
    margin-left: auto
    display: flex
    align-items: center
    justify-content: center

  .is-loading
    opacity: 0.7
    cursor: wait

  .loading-spinner
    display: inline-block
    width: 12px
    height: 12px
    border: 2px solid rgba(0, 0, 0, 0.1)
    border-top-color: #3498db
    border-radius: 50%
    animation: spin 1s linear infinite

@keyframes spin
  0%
    transform: rotate(0deg)
  100%
    transform: rotate(360deg)
</style>
