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
  <div class="p-2.5 max-w-xs" data-cy="score-popup">
    <div class="flex justify-between">
      <div class="flex-grow mr-1.25">
        <score-label :score="score" :label="`${score}/10`" size="huge" />
      </div>
      <div class="flex-grow ml-1.25">
        <h3 class="font-accent text-lg">{{ label }}</h3>
      </div>
    </div>
    <div class="text-[var(--color-light-green)] text-right">
      {{ lat.toFixed(2) }}° N, {{ lng.toFixed(2) }}° E
    </div>
  </div>
</template>
