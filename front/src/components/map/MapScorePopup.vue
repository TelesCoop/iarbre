<script setup lang="ts">
import ScoreLabel from "./ScoreLabel.vue"
import { computed } from "vue"

const props = defineProps({
  score: {
    required: true,
    type: Number
  },
  lat: {
    required: true,
    type: Number
  },
  lng: {
    required: true,
    type: Number
  }
})

const label = computed(() => {
  if (props.score >= 5) return "Plantabilité élevée"
  return "Plantabilité faible"
})
</script>

<template>
  <div class="popover" data-cy="score-popup">
    <div class="columns">
      <div class="left">
        <score-label :score="score" :label="`${score}/10`" size="huge" />
      </div>
      <div class="right">
        <h3 class="title">{{ label }}</h3>
      </div>
    </div>
    <div class="text-light-green text-right">{{ lat.toFixed(2) }}° N, {{ lng.toFixed(2) }}° E</div>
  </div>
</template>

<style lang="sass" scoped>
.popover
  padding: 10px

  .columns
      .left
        flex-grow: 1
        margin-right: 5px

      .right
        flex-grow: 2
        margin-left: 5px

      justify-content: space-between
      display: flex
      flex-direction: row
  max-width: 400px // also defined in `stores/map.ts::setupTile`

.title
    font-family: $accent-font
    font-size: 1.2rem
</style>
