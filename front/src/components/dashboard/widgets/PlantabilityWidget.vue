<script lang="ts" setup>
import { computed } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import type { DashboardPlantability } from "@/types/dashboard"
import {
  META_FACTOR_COLORS,
  PLANTABILITY_COLOR_MAP,
  PlantabilityScoreThreshold
} from "@/utils/plantability"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"

const PLANTABILITY_MAX_SCORE = PlantabilityScoreThreshold.VERY_FAVORED
const META_FACTOR_MAX = 55

interface Props {
  data: DashboardPlantability
}

const props = defineProps<Props>()

const score = computed(() => Math.round(props.data.averageNormalizedIndice * 10) / 10)
const arcColor = computed(() => {
  const idx = PLANTABILITY_COLOR_MAP.indexOf(Math.round(score.value))
  if (idx !== -1 && idx + 1 < PLANTABILITY_COLOR_MAP.length) {
    return String(PLANTABILITY_COLOR_MAP[idx + 1])
  }
  return "#426A45"
})

const getColorForScore = (scoreValue: number): string => {
  const idx = PLANTABILITY_COLOR_MAP.indexOf(scoreValue)
  if (idx !== -1 && idx + 1 < PLANTABILITY_COLOR_MAP.length) {
    return String(PLANTABILITY_COLOR_MAP[idx + 1])
  }
  return "#C4C4C4"
}

const bars = computed(() => {
  const distribution = props.data.distribution
  const entries = Object.keys(distribution)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => ({
      label: k,
      value: distribution[k],
      color: getColorForScore(Number(k))
    }))
  const total = entries.reduce((a, b) => a + b.value, 0)
  return entries.map((e) => ({ ...e, pct: total > 0 ? e.value / total : 0 }))
})

const metaFactorBars = computed(() => {
  const mf = props.data.metaFactors
  if (!mf) return []
  return Object.entries(mf).map(([label, value]) => ({
    label,
    value,
    color: META_FACTOR_COLORS[label] ?? "#C4C4C4",
    display: `${value.toFixed(1)}%`
  }))
})

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const pctH = 16
    const barH = Math.min(height * 0.45, 30)
    const labelH = 16
    const chartTotalH = pctH + barH + labelH
    const offsetY = Math.max((height - chartTotalH) / 2, 0)
    const barY = pctH
    const labelY = barY + barH + labelH - 2
    const gap = 1.5

    const g = svg.append("g").attr("transform", `translate(0,${offsetY})`)

    let xOffset = 0
    const segments = bars.value.map((b) => {
      const w = Math.max(b.pct * width - gap, 0)
      const seg = { ...b, x: xOffset, w }
      xOffset += w + gap
      return seg
    })

    g.selectAll(".marimekko-seg")
      .data(segments)
      .join("rect")
      .attr("class", "marimekko-seg")
      .attr("x", (d) => d.x)
      .attr("y", barY)
      .attr("height", barH)
      .attr("rx", 4)
      .attr("fill", (d) => d.color)
      .attr("opacity", 0.85)
      .attr("width", animate ? 0 : (d) => d.w)
      .on("mouseenter", function () {
        d3.select(this).attr("opacity", 1)
      })
      .on("mouseleave", function () {
        d3.select(this).attr("opacity", 0.85)
      })

    if (animate) {
      g.selectAll(".marimekko-seg")
        .transition()
        .duration(700)
        .delay((_, i) => i * 50)
        .ease(d3.easeCubicOut)
        .attr("width", (d) => (d as (typeof segments)[0]).w)
    }

    g.selectAll(".seg-pct")
      .data(segments.filter((s) => s.pct >= 0.06))
      .join("text")
      .attr("class", "seg-pct")
      .attr("x", (d) => d.x + d.w / 2)
      .attr("y", barY - 4)
      .attr("text-anchor", "middle")
      .attr("font-size", "0.5625rem")
      .style("fill", "var(--color-gray-500)")
      .attr("opacity", animate ? 0 : 1)
      .text((d) => `${(d.pct * 100).toFixed(0)}%`)

    if (animate) {
      g.selectAll(".seg-pct").transition().delay(700).duration(300).attr("opacity", 1)
    }

    g.selectAll(".seg-label")
      .data(segments.filter((s) => s.pct >= 0.06))
      .join("text")
      .attr("class", "seg-label")
      .attr("x", (d) => d.x + d.w / 2)
      .attr("y", labelY)
      .attr("text-anchor", "middle")
      .attr("font-size", "0.5625rem")
      .style("fill", "var(--color-gray-400)")
      .text((d) => d.label)
  },
  [bars]
)
</script>

<template>
  <DashboardWidgetCard subtitle="Indice moyen de plantabilité" title="Plantabilité">
    <div class="widget-body">
      <div class="score-col">
        <DashboardArcScore
          :color="arcColor"
          :max-value="PLANTABILITY_MAX_SCORE"
          :size="150"
          :value="score"
          label="plantabilité"
        />
        <svg ref="svgRef" class="distribution-chart" />
      </div>
      <div class="meta-factors">
        <div v-for="bar in metaFactorBars" :key="bar.label" class="bar-item">
          <span class="bar-label">{{ bar.label }}</span>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{
                width: `${Math.min((bar.value / META_FACTOR_MAX) * 100, 100)}%`,
                backgroundColor: bar.color
              }"
            >
              <span class="bar-inner-value">{{ bar.display }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-col gap-4 flex-1 w-full;
}

.score-col {
  @apply flex flex-row items-center gap-4 shrink-0 w-full;
}

.distribution-chart {
  @apply flex-1 h-20;
}

.meta-factors {
  @apply flex flex-col gap-1.5;
}

.bar-item {
  @apply flex flex-col gap-0.5;
}

.bar-label {
  @apply text-[0.625rem] text-gray-500 uppercase tracking-wide;
}

.bar-track {
  @apply w-full h-6 bg-gray-100 rounded-md overflow-hidden;
}

.bar-fill {
  @apply h-full rounded-md flex items-center px-2;
  animation: barGrow 700ms ease-out both;
}

.bar-inner-value {
  @apply text-[0.625rem] font-bold text-white whitespace-nowrap;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>
