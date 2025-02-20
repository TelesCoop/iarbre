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
  else return "Plantabilité faible"
})
</script>

<template>
  <div class="popover">
    <div class="columns">
      <div class="left">
        <score-label :score="4" label="4/10" size="huge" />
      </div>
      <div class="right">
        <h3 class="title">{{ label }}</h3>
        <button class="button primary">Voir les détails</button>
      </div>
    </div>
    <div class="text-light-green">{{ lat }}° N, {{ lng }}° E <button>(copy)</button></div>
  </div>
</template>

<style lang="sass" scoped>
.popover
    padding: 10px

    .columns
        .left
            flex-grow: 1

        .right
            flex-grow: 2

        display: flex
        flex-direction: row


.title
    font: $accent-font
</style>
