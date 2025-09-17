<script lang="ts" setup>
import { computed } from "vue"
import ContextDataScore from "@/components/contextData/shared/ContextDataScore.vue"
import type { ContextDataScoreConfig } from "@/types/contextData"

interface PlantabilityScoreProps {
  score: number
  percentage: number
}

const props = defineProps<PlantabilityScoreProps>()

const scoreConfig = computed(
  (): ContextDataScoreConfig => ({
    score: props.score,
    maxScore: 10,
    percentage: props.percentage,
    label: "plantabilité",
    colorScheme: "plantability"
  })
)
</script>

<template>
  <context-data-score v-bind="scoreConfig" />
</template>
