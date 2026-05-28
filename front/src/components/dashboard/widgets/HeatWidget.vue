<script lang="ts" setup>
import { computed, ref, type Ref } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import type { DashboardVulnerability } from "@/types/dashboard"
import { HEAT_COLORS } from "@/utils/dashboardColors"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"
import { vulnerabilityScore, VulnerabilityType } from "@/utils/vulnerability"

const VULNERABILITY_MAX_SCORE = vulnerabilityScore.TOTAL
const POLAR_MAX_SCORE = vulnerabilityScore[VulnerabilityType.EXPOSITION]

interface Props {
  data: DashboardVulnerability
}

const props = defineProps<Props>()

type AxisData = { lines: string[]; value: number; color: string }
type HoveredAxis = { label: string; value: number; color: string; level: string } | null

function buildAxes(
  expo: number,
  sensibility: number,
  capaf: number,
  palette: { expo: string; sensibility: string; capaf: string }
): AxisData[] {
  return [
    { lines: ["Exposition"], value: expo, color: palette.expo },
    { lines: ["Sensibilité"], value: sensibility, color: palette.sensibility },
    { lines: ["Difficulté à", "faire face"], value: capaf, color: palette.capaf }
  ]
}

const dayAxes = computed(() =>
  buildAxes(props.data.expoDay, props.data.sensibilityDay, props.data.capafDay, HEAT_COLORS.day)
)

const nightAxes = computed(() =>
  buildAxes(
    props.data.expoNight,
    props.data.sensibilityNight,
    props.data.capafNight,
    HEAT_COLORS.night
  )
)

const dayCurrentRatios = ref([0, 0, 0])
const dayHoveredAxis = ref<HoveredAxis>(null)
const dayTooltipPos = ref({ x: 0, y: 0 })

const nightCurrentRatios = ref([0, 0, 0])
const nightHoveredAxis = ref<HoveredAxis>(null)
const nightTooltipPos = ref({ x: 0, y: 0 })

function getLevel(value: number): string {
  if (value < 1) return "Faible"
  if (value < 2) return "Modéré"
  return "Élevé"
}

// https://gist.github.com/nbremer/21746a9668ffdf6d8242
function drawSpiderChart(
  { svg, width, height }: D3ChartContext,
  animate: boolean,
  axes: AxisData[],
  accentColor: string,
  currentRatios: Ref<number[]>,
  hoveredAxis: Ref<HoveredAxis>,
  tooltipPos: Ref<{ x: number; y: number }>,
  svgEl: SVGSVGElement
) {
  const size = Math.min(width, height)
  if (size <= 0) return

  const cx = width / 2
  const cy = height / 2
  const radius = size / 2 - 34
  const numAxes = axes.length
  const angleSlice = (2 * Math.PI) / numAxes
  const rScale = d3.scaleLinear().range([0, radius]).domain([0, POLAR_MAX_SCORE])

  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

  function polyPoints(ratios: number[]): string {
    return ratios
      .map((r, i) => {
        const angle = angleSlice * i - Math.PI / 2
        const rv = rScale(r * POLAR_MAX_SCORE)
        return `${rv * Math.cos(angle)},${rv * Math.sin(angle)}`
      })
      .join(" ")
  }

  for (let level = 1; level <= POLAR_MAX_SCORE; level++) {
    const r = rScale(level)
    const pts = d3.range(numAxes).map((i) => {
      const angle = angleSlice * i - Math.PI / 2
      return `${r * Math.cos(angle)},${r * Math.sin(angle)}`
    })
    g.append("polygon")
      .attr("points", pts.join(" "))
      .attr("fill", level === POLAR_MAX_SCORE ? "#f9fafb" : "none")
      .attr("stroke", "#e5e7eb")
      .attr("stroke-width", 1)
  }

  axes.forEach((_, i) => {
    const angle = angleSlice * i - Math.PI / 2
    g.append("line")
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", rScale(POLAR_MAX_SCORE) * Math.cos(angle))
      .attr("y2", rScale(POLAR_MAX_SCORE) * Math.sin(angle))
      .attr("stroke", "#e5e7eb")
      .attr("stroke-width", 1)
  })

  const targetRatios = axes.map((a) => Math.min(Math.max(a.value / POLAR_MAX_SCORE, 0), 1))
  const startRatios = animate ? currentRatios.value.slice() : targetRatios

  const blobFill = g
    .append("polygon")
    .attr("points", polyPoints(startRatios))
    .attr("fill", accentColor)
    .attr("fill-opacity", 0.25)

  const blobStroke = g
    .append("polygon")
    .attr("points", polyPoints(startRatios))
    .attr("fill", "none")
    .attr("stroke", accentColor)
    .attr("stroke-width", 2)

  if (animate) {
    const tween = () => (t: number) =>
      polyPoints(startRatios.map((s, i) => s + (targetRatios[i] - s) * t))
    blobFill.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
    blobStroke.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
  }

  currentRatios.value = targetRatios

  axes.forEach((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const ratio = targetRatios[i]
    const r = rScale(ratio * POLAR_MAX_SCORE)
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
        hoveredAxis.value = {
          label: axis.lines.join(" "),
          value: axis.value,
          color: axis.color,
          level: getLevel(axis.value)
        }
        const wrapperRect = svgEl.closest(".spider-wrapper")?.getBoundingClientRect()
        if (wrapperRect) {
          tooltipPos.value = {
            x: event.clientX - wrapperRect.left,
            y: event.clientY - wrapperRect.top - 44
          }
        }
      })
      .on("mousemove", (event: MouseEvent) => {
        const wrapperRect = svgEl.closest(".spider-wrapper")?.getBoundingClientRect()
        if (!wrapperRect) return
        tooltipPos.value = {
          x: event.clientX - wrapperRect.left,
          y: event.clientY - wrapperRect.top - 44
        }
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
      .attr("font-size", "9px")
      .attr("fill", "#9CA3AF")

    axis.lines.forEach((line, lineIndex) => {
      labelText
        .append("tspan")
        .attr("x", 0)
        .attr("dy", lineIndex === 0 ? 0 : "1.1em")
        .text(line)
    })

    labelG
      .append("text")
      .attr("text-anchor", anchor)
      .attr("dominant-baseline", baseline)
      .attr("dy", `${axis.lines.length * 1.2}em`)
      .attr("font-size", "10px")
      .attr("font-weight", "600")
      .attr("fill", "#374151")
      .text(`${axis.value.toFixed(1)}/${POLAR_MAX_SCORE}`)
  })
}

const { svgRef: daySvgRef } = useD3Chart(
  (ctx: D3ChartContext, animate: boolean) => {
    drawSpiderChart(
      ctx,
      animate,
      dayAxes.value,
      HEAT_COLORS.day.accent,
      dayCurrentRatios,
      dayHoveredAxis,
      dayTooltipPos,
      daySvgRef.value!
    )
  },
  [dayAxes]
)

const { svgRef: nightSvgRef } = useD3Chart(
  (ctx: D3ChartContext, animate: boolean) => {
    drawSpiderChart(
      ctx,
      animate,
      nightAxes.value,
      HEAT_COLORS.night.accent,
      nightCurrentRatios,
      nightHoveredAxis,
      nightTooltipPos,
      nightSvgRef.value!
    )
  },
  [nightAxes]
)
</script>

<template>
  <DashboardWidgetCard
    subtitle="Vulnérabilité aux températures extrêmes"
    title="Étude sur l'exposition, la difficulté à faire face et la sensibilité par îlot"
  >
    <div class="widget-body">
      <div class="scores-col">
        <div class="score-block">
          <span class="score-mode-label">Jour</span>
          <DashboardArcScore
            :color="HEAT_COLORS.day.accent"
            :max-value="VULNERABILITY_MAX_SCORE"
            :value="props.data.averageDay"
            :size="90"
          />
        </div>
        <div class="score-block">
          <span class="score-mode-label">Nuit</span>
          <DashboardArcScore
            :color="HEAT_COLORS.night.accent"
            :max-value="VULNERABILITY_MAX_SCORE"
            :value="props.data.averageNight"
            :size="90"
          />
        </div>
      </div>

      <div class="spiders-col">
        <div class="spider-block">
          <span class="spider-mode-label">Jour</span>
          <div class="spider-wrapper">
            <svg ref="daySvgRef" width="100%" height="100%" style="overflow: visible" />
            <div
              v-if="dayHoveredAxis"
              class="chart-tooltip"
              :style="{ left: `${dayTooltipPos.x}px`, top: `${dayTooltipPos.y}px` }"
            >
              <span class="tooltip-dot" :style="{ backgroundColor: dayHoveredAxis.color }" />
              <span class="tooltip-label">{{ dayHoveredAxis.label }}</span>
              <span class="tooltip-value"
                >{{ dayHoveredAxis.value.toFixed(1) }}/{{ POLAR_MAX_SCORE }}</span
              >
              <span class="tooltip-sep">-</span>
              <span class="tooltip-level">{{ dayHoveredAxis.level }}</span>
            </div>
          </div>
        </div>
        <div class="spider-block">
          <span class="spider-mode-label">Nuit</span>
          <div class="spider-wrapper">
            <svg ref="nightSvgRef" width="100%" height="100%" style="overflow: visible" />
            <div
              v-if="nightHoveredAxis"
              class="chart-tooltip"
              :style="{ left: `${nightTooltipPos.x}px`, top: `${nightTooltipPos.y}px` }"
            >
              <span class="tooltip-dot" :style="{ backgroundColor: nightHoveredAxis.color }" />
              <span class="tooltip-label">{{ nightHoveredAxis.label }}</span>
              <span class="tooltip-value"
                >{{ nightHoveredAxis.value.toFixed(1) }}/{{ POLAR_MAX_SCORE }}</span
              >
              <span class="tooltip-sep">-</span>
              <span class="tooltip-level">{{ nightHoveredAxis.level }}</span>
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
  @apply flex flex-row gap-4;
}

.scores-col {
  @apply flex flex-col gap-6 items-center justify-center shrink-0;
}

.score-block {
  @apply flex flex-col items-center gap-1;
}

.score-mode-label {
  @apply text-xs font-medium text-gray-500;
}

.spiders-col {
  @apply flex-1 flex flex-row gap-2 items-start;
}

.spider-block {
  @apply flex-1 flex flex-col items-center gap-1;
}

.spider-mode-label {
  @apply text-xs font-medium text-gray-500;
}

.spider-wrapper {
  @apply relative flex items-center justify-center w-full aspect-square;
}
</style>
