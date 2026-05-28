<script lang="ts" setup>
import { computed } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
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

const aboveThresholdPct = computed(() => {
  const entries = Object.entries(props.data.distribution)
  const total = entries.reduce((s, [, v]) => s + v, 0)
  if (total === 0) return 0
  const above = entries.filter(([k]) => +k > 25).reduce((s, [, v]) => s + v, 0)
  return Math.round((above / total) * 1000) / 10
})

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

function colorForIndice(indice: number): string {
  let color = coloredSegments[0].color
  for (const seg of coloredSegments) {
    if (indice >= seg.min) color = seg.color
  }
  return color
}

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const entries = Object.entries(props.data.distribution)
      .map(([k, v]) => ({ indice: +k, count: +v }))
      .sort((a, b) => a.indice - b.indice)

    if (entries.length === 0) return

    const margin = { top: 16, right: 4, bottom: 16, left: 0 }
    const innerW = width - margin.left - margin.right
    const innerH = height - margin.top - margin.bottom

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    const maxCount = d3.max(entries, (d) => d.count) ?? 1
    const xScale = d3.scaleLinear().domain([0, BIOSPHERE_MAX_SCORE]).range([0, innerW])
    const yScale = d3.scaleLinear().domain([0, maxCount]).range([innerH, 0])
    const barW = innerW / (BIOSPHERE_MAX_SCORE + 1)

    const THRESHOLD = 25
    const thresholdX = xScale(THRESHOLD)
    g.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", thresholdX)
      .attr("height", innerH)
      .attr("fill", "#d73026")
      .attr("opacity", 0.06)

    const bars = g
      .selectAll<SVGRectElement, { indice: number; count: number }>(".bar")
      .data(entries)
      .join("rect")
      .attr("class", "bar")
      .attr("x", (d) => xScale(d.indice))
      .attr("y", animate ? innerH : (d) => yScale(d.count))
      .attr("width", Math.max(barW - 0.5, 1))
      .attr("height", animate ? 0 : (d) => innerH - yScale(d.count))
      .attr("fill", (d) => colorForIndice(d.indice))
      .attr("opacity", 0.85)

    if (animate) {
      bars
        .transition()
        .duration(700)
        .ease(d3.easeCubicOut)
        .attr("y", (d) => yScale(d.count))
        .attr("height", (d) => innerH - yScale(d.count))
    }

    g.append("line")
      .attr("x1", thresholdX)
      .attr("x2", thresholdX)
      .attr("y1", 0)
      .attr("y2", innerH)
      .attr("stroke", "#6B7280")
      .attr("stroke-width", 1)

    g.append("text")
      .attr("x", thresholdX + 4)
      .attr("y", 10)
      .attr("text-anchor", "start")
      .attr("font-size", "0.625rem")
      .attr("fill", "#6B7280")
      .text(`${aboveThresholdPct.value}% > 25`)

    const meanX = xScale(score.value)
    g.append("line")
      .attr("x1", meanX)
      .attr("x2", meanX)
      .attr("y1", 0)
      .attr("y2", innerH)
      .attr("stroke", arcColor.value)
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "3,2")

    const labelAnchor = score.value > 50 ? "end" : "start"
    const labelOffset = score.value > 50 ? -4 : 4
    g.append("text")
      .attr("x", meanX + labelOffset)
      .attr("y", 10)
      .attr("text-anchor", labelAnchor)
      .attr("font-size", "0.625rem")
      .attr("fill", arcColor.value)
      .attr("font-weight", "600")
      .text(`Valeur moyenne : ${score.value}%`)

    ticks.forEach((t) => {
      const isThreshold = t === THRESHOLD
      g.append("text")
        .attr("x", xScale(t))
        .attr("y", innerH + 13)
        .attr("text-anchor", t === 0 ? "start" : t === BIOSPHERE_MAX_SCORE ? "end" : "middle")
        .attr("font-size", isThreshold ? "0.625rem" : "0.5625rem")
        .attr("font-weight", isThreshold ? "600" : "400")
        .attr("fill", isThreshold ? "#6B7280" : "#9CA3AF")
        .text(t)
    })
  },
  [score, arcColor, aboveThresholdPct, () => props.data.distribution]
)
</script>

<template>
  <DashboardWidgetCard
    subtitle="Décris la part des surfaces maitrisées par l'Homme et les surfaces naturelles."
    title="Indice moyen d'intégrité fonctionnelle de la biosphère"
  >
    <svg ref="svgRef" class="w-full min-h-24" />
  </DashboardWidgetCard>
</template>
