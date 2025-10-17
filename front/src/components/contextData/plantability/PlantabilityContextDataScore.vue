<script lang="ts" setup>
import CircularScore from "@/components/shared/CircularScore.vue"
import type { CircularScoreSize } from "@/types/contextData"

interface PlantabilityScoreProps {
  score: number
  percentage: number
  size?: CircularScoreSize
}

defineProps<PlantabilityScoreProps>()
</script>

<template>
  <circular-score
    :score="score"
    :max-score="10"
    :percentage="percentage"
    :size="size"
    label="plantabilité"
    color-scheme="plantability"
  />
</template>
