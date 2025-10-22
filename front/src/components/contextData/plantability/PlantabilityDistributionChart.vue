<script lang="ts" setup>
import { computed } from "vue"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"

interface DistributionEntry {
  score: number
  count: number
}

interface PlantabilityDistributionChartProps {
  entries: DistributionEntry[]
  title?: string
  showLegend?: boolean
  showDetails?: boolean
}

const props = withDefaults(defineProps<PlantabilityDistributionChartProps>(), {
  title: "Distribution des scores de plantabilité sur la zone.",
  showLegend: true,
  showDetails: true
})

const chartData = computed(() => {
  if (!props.entries || props.entries.length === 0) return null

  const sortedEntries = [...props.entries].sort((a, b) => a.score - b.score)
  const labels = sortedEntries.map((entry) => `${entry.score}/10`)
  const data = sortedEntries.map((entry) => entry.count)

  // Map each score to its corresponding color from PLANTABILITY_COLOR_MAP
  const backgroundColor = sortedEntries.map((entry) => {
    const colorIndex = PLANTABILITY_COLOR_MAP.indexOf(entry.score)
    return colorIndex !== -1 && colorIndex + 1 < PLANTABILITY_COLOR_MAP.length
      ? PLANTABILITY_COLOR_MAP[colorIndex + 1]
      : "#C4C4C4"
  })

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor,
        borderWidth: 2,
        borderColor: "#fff"
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: props.showLegend,
      position: "bottom",
      onClick: null // don't allow filtering onClick
    },
    title: {
      display: true,
      text: props.title
    },
    font: {
      size: 34,
      family: "IBM Plex Mono"
    }
  }
}))
</script>

<template>
  <div v-if="chartData" class="p-4">
    <Chart type="pie" :data="chartData" :options="chartOptions" class="w-full h-64" />
    <p v-if="showDetails" class="text-sm font-sans text-center m-2">
      0/10 signifie non plantable et 10/10 plantable
    </p>
  </div>
</template>
