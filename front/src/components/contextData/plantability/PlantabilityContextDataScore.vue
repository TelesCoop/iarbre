<script lang="ts" setup>
interface PlantabilityScoreProps {
  score: number
  percentage: number
}

defineProps<PlantabilityScoreProps>()
</script>

<template>
  <section class="text-center" aria-labelledby="score-section">
    <h3 id="score-section" class="sr-only">Score de plantabilité</h3>

    <div class="relative inline-block">
      <circular-progress
        :percentage="percentage"
        :aria-label="`Score de plantabilité: ${score} sur 10`"
      />

      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-sm text-gray-600">Score :</span>
        <span class="text-3xl font-bold text-gray-800"> {{ score }}/10 </span>
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
