<script setup lang="ts">
import ScoreLabel from "@/components/map/ScoreLabel.vue"
import { computed } from "vue"

const props = defineProps({
  index: {
    required: true,
    type: Number
  }
})

const index = computed(() => Math.round(10 * props.index))

const label = computed(() => {
  if (index.value >= 5) return "Plantabilité élevée"
  return "Plantabilité faible"
})
</script>

<template>
  <div data-cy="plantability-score-popup" class="p-2.5 max-w-xs">
    <div class="flex-grow mr-1.25">
      <score-label :score="index" :label="`${index}/10`" size="huge" />
    </div>
    <div class="flex-grow ml-1.25">
      <h3 class="font-accent text-lg">{{ label }}</h3>
    </div>
  </div>
</template>
