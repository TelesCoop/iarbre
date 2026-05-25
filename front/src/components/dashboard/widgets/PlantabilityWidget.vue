<script lang="ts" setup>
import { computed, ref } from "vue"
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
const SPIDER_MAX = 55

const LABEL_LINES: Record<string, string[]> = {
  "Réseaux et infrastructures": ["Réseaux &", "infrastr."],
  "Infrastructure de transport": ["Transport &", "mobilité"],
  Bâtiments: ["Bâtiments"],
  "Espaces verts": ["Espaces verts"],
  "Aménagements urbains": ["Aménag.", "urbains"],
  "Plan d'eau": ["Plan d'eau"],
  "Espaces artificialisés": ["Esp.", "artificialisés"]
}

interface Props {
  data: DashboardPlantability
}

const props = defineProps<Props>()

type AxisData = { lines: string[]; value: number; color: string }
type HoveredAxis = { label: string; value: number; color: string } | null

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

const spiderAxes = computed<AxisData[]>(() => {
  const mf = props.data.metaFactors

  if (!mf) return []
  return Object.entries(mf).map(([label, value]) => ({
    lines: LABEL_LINES[label] ?? [label],
    value,
    color: META_FACTOR_COLORS[label] ?? "#C4C4C4"
  }))
})

const spiderCurrentRatios = ref<number[]>([])
const hoveredAxis = ref<HoveredAxis>(null)
const tooltipPos = ref({ x: 0, y: 0 })

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
      .attr("font-size", "9px")
      .attr("fill", "#6B7280")
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
      .attr("font-size", "9px")
      .attr("fill", "#9CA3AF")
      .text((d) => d.label)
  },
  [bars]
)

const { svgRef: spiderSvgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const axes = spiderAxes.value
    if (axes.length === 0) return

    const size = Math.min(width, height)
    if (size <= 0) return

    const cx = width / 2
    const cy = height / 2
    const radius = size / 2 - 38
    const numAxes = axes.length
    const angleSlice = (2 * Math.PI) / numAxes
    const rScale = d3.scaleLinear().range([0, radius]).domain([0, SPIDER_MAX])

    const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

    function polyPoints(ratios: number[]): string {
      return ratios
        .map((r, i) => {
          const angle = angleSlice * i - Math.PI / 2
          const rv = rScale(r * SPIDER_MAX)
          return `${rv * Math.cos(angle)},${rv * Math.sin(angle)}`
        })
        .join(" ")
    }

    for (let level = 1; level <= 4; level++) {
      const r = rScale((level / 4) * SPIDER_MAX)
      const pts = d3.range(numAxes).map((i) => {
        const angle = angleSlice * i - Math.PI / 2
        return `${r * Math.cos(angle)},${r * Math.sin(angle)}`
      })
      g.append("polygon")
        .attr("points", pts.join(" "))
        .attr("fill", level === 4 ? "#f9fafb" : "none")
        .attr("stroke", "#e5e7eb")
        .attr("stroke-width", 1)
    }

    axes.forEach((_, i) => {
      const angle = angleSlice * i - Math.PI / 2
      g.append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", rScale(SPIDER_MAX) * Math.cos(angle))
        .attr("y2", rScale(SPIDER_MAX) * Math.sin(angle))
        .attr("stroke", "#e5e7eb")
        .attr("stroke-width", 1)
    })

    const targetRatios = axes.map((a) => Math.min(Math.max(a.value / SPIDER_MAX, 0), 1))
    const startRatios = animate ? spiderCurrentRatios.value.slice() : targetRatios

    const blobFill = g
      .append("polygon")
      .attr("points", polyPoints(startRatios))
      .attr("fill", arcColor.value)
      .attr("fill-opacity", 0.2)

    const blobStroke = g
      .append("polygon")
      .attr("points", polyPoints(startRatios))
      .attr("fill", "none")
      .attr("stroke", arcColor.value)
      .attr("stroke-width", 2)

    if (animate) {
      const tween = () => (t: number) =>
        polyPoints(startRatios.map((s, i) => s + (targetRatios[i] - s) * t))
      blobFill.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
      blobStroke.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
    }

    spiderCurrentRatios.value = targetRatios

    axes.forEach((axis, i) => {
      const angle = angleSlice * i - Math.PI / 2
      const ratio = targetRatios[i]
      const r = rScale(ratio * SPIDER_MAX)
      const dotX = r * Math.cos(angle)
      const dotY = r * Math.sin(angle)

      const dotG = g.append("g").attr("class", "dot-group")
      dotG
        .append("circle")
        .attr("cx", dotX)
        .attr("cy", dotY)
        .attr("r", 4)
        .attr("fill", axis.color)
        .attr("stroke", "white")
        .attr("stroke-width", 1.5)

      dotG
        .append("circle")
        .attr("cx", dotX)
        .attr("cy", dotY)
        .attr("r", 10)
        .attr("fill", "transparent")
        .style("cursor", "pointer")
        .on("mouseenter", function (event: MouseEvent) {
          g.selectAll<SVGGElement, unknown>(".dot-group circle:first-child")
            .transition()
            .duration(150)
            .attr("opacity", 0.3)
          d3.select(this.parentNode as Element)
            .select("circle")
            .transition()
            .duration(150)
            .attr("opacity", 1)
          hoveredAxis.value = { label: axis.lines.join(" "), value: axis.value, color: axis.color }
          const rect = spiderSvgRef.value?.closest(".spider-wrapper")?.getBoundingClientRect()
          if (rect)
            tooltipPos.value = { x: event.clientX - rect.left, y: event.clientY - rect.top - 44 }
        })
        .on("mousemove", (event: MouseEvent) => {
          const rect = spiderSvgRef.value?.closest(".spider-wrapper")?.getBoundingClientRect()
          if (rect)
            tooltipPos.value = { x: event.clientX - rect.left, y: event.clientY - rect.top - 44 }
        })
        .on("mouseleave", function () {
          g.selectAll<SVGGElement, unknown>(".dot-group circle:first-child")
            .transition()
            .duration(200)
            .attr("opacity", 1)
          hoveredAxis.value = null
        })

      const labelR = radius + 16
      const lx = labelR * Math.cos(angle)
      const ly = labelR * Math.sin(angle)
      const cosA = Math.cos(angle)
      const anchor = cosA > 0.2 ? "start" : cosA < -0.2 ? "end" : "middle"
      const sinA = Math.sin(angle)
      const baseline = sinA < -0.5 ? "auto" : sinA > 0.5 ? "hanging" : "central"

      const labelG = g.append("g").attr("transform", `translate(${lx},${ly})`)
      const labelText = labelG
        .append("text")
        .attr("text-anchor", anchor)
        .attr("dominant-baseline", baseline)
        .attr("font-size", "8px")
        .attr("fill", "#9CA3AF")

      axis.lines.forEach((line, li) => {
        labelText
          .append("tspan")
          .attr("x", 0)
          .attr("dy", li === 0 ? 0 : "1.1em")
          .text(line)
      })

      labelG
        .append("text")
        .attr("text-anchor", anchor)
        .attr("dominant-baseline", baseline)
        .attr("dy", `${axis.lines.length * 1.2}em`)
        .attr("font-size", "9px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(`${axis.value.toFixed(1)}%`)
    })
  },
  [spiderAxes, arcColor]
)
</script>

<template>
  <DashboardWidgetCard subtitle="Indice moyen de plantabilité" title="Plantabilité">
    <div class="widget-body">
      <div class="score-col">
        <DashboardArcScore
          :color="arcColor"
          :max-value="PLANTABILITY_MAX_SCORE"
          :value="score"
          label="plantabilité"
        />
        <svg ref="svgRef" class="distribution-chart" />
      </div>
      <div class="spider-col">
        <div class="spider-wrapper">
          <svg ref="spiderSvgRef" width="100%" height="100%" style="overflow: visible" />
          <div
            v-if="hoveredAxis"
            class="chart-tooltip"
            :style="{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y}px` }"
          >
            <span class="tooltip-dot" :style="{ backgroundColor: hoveredAxis.color }" />
            <span class="tooltip-label">{{ hoveredAxis.label }}</span>
            <span class="tooltip-value">{{ hoveredAxis.value.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-col gap-6 flex-1 w-full;
}

.score-col {
  @apply flex flex-row items-center gap-4 shrink-0 w-full;
}

.distribution-chart {
  @apply flex-1 h-12;
}

.spider-col {
  @apply flex-1 flex flex-col min-h-[160px];
}

.spider-wrapper {
  @apply relative flex-1 w-full;
}
</style>
