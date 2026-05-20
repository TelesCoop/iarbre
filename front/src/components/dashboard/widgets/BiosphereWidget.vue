<script lang="ts" setup>
import { computed } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import type { DashboardBiosphere } from "@/types/dashboard"
import {
  BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP,
  BIOSPHERE_INTEGRITY_RANGES,
  BiosphereIntegrityLegendName
} from "@/utils/biosphere_functional_integrity"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"

const BIOSPHERE_MAX_SCORE = 100

interface Props {
  data: DashboardBiosphere
}

const props = defineProps<Props>()

const coloredSegments = Object.values(BIOSPHERE_INTEGRITY_RANGES).map(([min, max], i) => ({
  min,
  max,
  color: String(BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP[2 + i * 2])
}))

const score = computed(() => Math.round(props.data.averageIndice * 10) / 10)

const arcColor = computed(() => {
  let color = coloredSegments[0].color
  for (const seg of coloredSegments) {
    if (score.value >= seg.min) color = seg.color
  }
  return color
})

const ticks = [
  0,
  ...Object.keys(BIOSPHERE_INTEGRITY_RANGES).map(
    (k) => BIOSPHERE_INTEGRITY_RANGES[k as BiosphereIntegrityLegendName][1]
  )
]

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const barH = Math.min(height * 0.4, 20)
    const markerH = 10
    const labelH = 14
    const totalH = markerH + barH + labelH
    const offsetY = Math.max((height - totalH) / 2, 0)
    const gap = 1.5

    const g = svg.append("g").attr("transform", `translate(0,${offsetY})`)

    let xOffset = 0
    const drawnSegs = coloredSegments.map((s) => {
      const w = Math.max(((s.max - s.min) / BIOSPHERE_MAX_SCORE) * width - gap, 0)
      const seg = { ...s, x: xOffset, w }
      xOffset += w + gap
      return seg
    })

    g.selectAll(".bio-seg")
      .data(drawnSegs)
      .join("rect")
      .attr("class", "bio-seg")
      .attr("x", (d) => d.x)
      .attr("y", markerH)
      .attr("height", barH)
      .attr("rx", 3)
      .attr("fill", (d) => d.color)
      .attr("opacity", 0.8)
      .attr("width", (d) => d.w)

    const markerX = (score.value / BIOSPHERE_MAX_SCORE) * width
    const marker = g
      .append("polygon")
      .attr("fill", arcColor.value)
      .attr("transform", animate ? "translate(0,0)" : `translate(${markerX},0)`)
      .attr("points", "-7,0 7,0 0,12")

    if (animate) {
      marker
        .transition()
        .duration(700)
        .ease(d3.easeCubicOut)
        .attr("transform", `translate(${markerX},0)`)
    }

    ticks.forEach((t) => {
      const tx = (t / BIOSPHERE_MAX_SCORE) * width
      g.append("text")
        .attr("x", tx)
        .attr("y", markerH + barH + labelH - 2)
        .attr("text-anchor", t === 0 ? "start" : t === BIOSPHERE_MAX_SCORE ? "end" : "middle")
        .attr("font-size", "9px")
        .attr("fill", "#9CA3AF")
        .text(t)
    })
  },
  [score, arcColor]
)
</script>

<template>
  <DashboardWidgetCard
    subtitle="Décris la part des surfaces maitrisées par l'Homme et les surfaces naturelles."
    title="Indice moyen d'intégrité fonctionnelle de la biosphère"
  >
    <div class="widget-body">
      <div class="score-col">
        <DashboardArcScore
          :color="arcColor"
          :max-value="BIOSPHERE_MAX_SCORE"
          :value="score"
          label="intégrité"
          :display-value="`${score}%`"
        />
      </div>
      <div class="chart-col">
        <svg ref="svgRef" width="100%" height="100%" />
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-row items-center gap-4;
}

.score-col {
  @apply flex flex-col items-center justify-center shrink-0;
}

.chart-col {
  @apply flex-1 min-h-20;
}
</style>
