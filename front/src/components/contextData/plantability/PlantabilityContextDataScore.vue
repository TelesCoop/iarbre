<script lang="ts" setup>
import { computed } from "vue"

interface PlantabilityScoreProps {
  score: number
  percentage: number
}

const props = defineProps<PlantabilityScoreProps>()

const textColor = computed(() => {
  if (!props.percentage) return "text-gray-800"
  return props.percentage >= 80
    ? "text-scale-8"
    : props.percentage >= 60
      ? "text-scale-4"
      : "text-scale-2"
})
</script>

<template>
  <section class="text-center" aria-labelledby="score-section">
    <h3 id="score-section" class="sr-only">Score de plantabilité</h3>

    <div class="relative inline-block">
      <circular-progress
        :percentage="percentage"
        :background-color="textColor"
        :aria-label="`Score de plantabilité: ${score} sur 10`"
        data-cy="circular-progress"
      />

      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-sm text-gray-600">Score :</span>
        <span class="text-xl md:text-3xl font-bold" :class="textColor" data-cy="plantability-score">
          {{ score }}/10
        </span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
