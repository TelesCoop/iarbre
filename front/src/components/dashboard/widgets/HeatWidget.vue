<script lang="ts" setup>
import { computed, ref } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"
import type { DashboardVulnerability } from "@/types/dashboard"
import { useDashboardStore } from "@/stores/dashboard"
import { HEAT_COLORS } from "@/utils/dashboardColors"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"
import { vulnerabilityScore, VulnerabilityType } from "@/utils/vulnerability"

const VULNERABILITY_MAX_SCORE = vulnerabilityScore.TOTAL
const POLAR_MAX_SCORE = vulnerabilityScore[VulnerabilityType.EXPOSITION]

interface Props {
  data: DashboardVulnerability
}

const props = defineProps<Props>()
const store = useDashboardStore()

const isDay = computed(() => store.heatMode === "day")
const palette = computed(() => (isDay.value ? HEAT_COLORS.day : HEAT_COLORS.night))

const axes = computed(() => {
  const expo = isDay.value ? props.data.expoDay : props.data.expoNight
  const sensibility = isDay.value ? props.data.sensibilityDay : props.data.sensibilityNight
  const capaf = isDay.value ? props.data.capafDay : props.data.capafNight
  return [
    { label: "Exposition", value: expo, color: palette.value.expo },
    { label: "Sensibilité", value: sensibility, color: palette.value.sensibility },
    { label: "Difficulté à faire face", value: capaf, color: palette.value.capaf }
  ]
})

const currentRatios = ref([0, 0, 0])
const hoveredAxis = ref<{ label: string; value: number; color: string; level: string } | null>(null)
const tooltipPos = ref({ x: 0, y: 0 })

function getLevel(value: number): string {
  if (value < 1) return "Faible"
  if (value < 2) return "Modéré"
  return "Élevé"
}

function updateTooltipPos(event: MouseEvent, svgEl: SVGSVGElement) {
  const wrapperRect = svgEl.closest(".spider-wrapper")?.getBoundingClientRect()
  if (!wrapperRect) return
  tooltipPos.value = {
    x: event.clientX - wrapperRect.left,
    y: event.clientY - wrapperRect.top - 44
  }
}

// https://gist.github.com/nbremer/21746a9668ffdf6d8242
const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const size = Math.min(width, height)
    if (size <= 0) return

    const cx = width / 2
    const cy = height / 2
    const radius = size / 2 - 34
    const numAxes = axes.value.length
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

    axes.value.forEach((_, i) => {
      const angle = angleSlice * i - Math.PI / 2
      g.append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", rScale(POLAR_MAX_SCORE) * Math.cos(angle))
        .attr("y2", rScale(POLAR_MAX_SCORE) * Math.sin(angle))
        .attr("stroke", "#e5e7eb")
        .attr("stroke-width", 1)
    })

    const targetRatios = axes.value.map((a) => Math.min(Math.max(a.value / POLAR_MAX_SCORE, 0), 1))
    const startRatios = animate ? currentRatios.value.slice() : targetRatios
    const blobColor = palette.value.accent

    const blobFill = g
      .append("polygon")
      .attr("points", polyPoints(startRatios))
      .attr("fill", blobColor)
      .attr("fill-opacity", 0.25)

    const blobStroke = g
      .append("polygon")
      .attr("points", polyPoints(startRatios))
      .attr("fill", "none")
      .attr("stroke", blobColor)
      .attr("stroke-width", 2)

    if (animate) {
      const tween = () => (t: number) =>
        polyPoints(startRatios.map((s, i) => s + (targetRatios[i] - s) * t))
      blobFill.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
      blobStroke.transition().duration(700).ease(d3.easeCubicOut).attrTween("points", tween)
    }

    currentRatios.value = targetRatios

    const svgEl = svgRef.value!
    axes.value.forEach((axis, i) => {
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
          hoveredAxis.value = { ...axis, level: getLevel(axis.value) }
          updateTooltipPos(event, svgEl)
        })
        .on("mousemove", (event: MouseEvent) => updateTooltipPos(event, svgEl))
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

      labelG
        .append("text")
        .attr("text-anchor", anchor)
        .attr("dominant-baseline", baseline)
        .attr("font-size", "9px")
        .attr("fill", "#9CA3AF")
        .text(axis.label)

      labelG
        .append("text")
        .attr("text-anchor", anchor)
        .attr("dominant-baseline", baseline)
        .attr("dy", "1.2em")
        .attr("font-size", "10px")
        .attr("font-weight", "600")
        .attr("fill", "#374151")
        .text(`${axis.value.toFixed(1)}/${POLAR_MAX_SCORE}`)
    })
  },
  [axes]
)
</script>

<template>
  <DashboardWidgetCard
    subtitle="Vulnérabilité aux températures extrêmes"
    title="Etude sur l'exposition, la difficulté à faire face et la sensibilité par îlot"
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

      <div class="polar-col">
        <div class="spider-wrapper">
          <svg ref="svgRef" width="100%" height="100%" style="overflow: visible" />
          <div
            v-if="hoveredAxis"
            class="chart-tooltip"
            :style="{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y}px` }"
          >
            <span class="tooltip-dot" :style="{ backgroundColor: hoveredAxis.color }" />
            <span class="tooltip-label">{{ hoveredAxis.label }}</span>
            <span class="tooltip-value"
              >{{ hoveredAxis.value.toFixed(1) }}/{{ POLAR_MAX_SCORE }}</span
            >
            <span class="tooltip-sep">-</span>
            <span class="tooltip-level">{{ hoveredAxis.level }}</span>
          </div>
        </div>
        <div class="toggle-row">
          <span :class="['toggle-label', { active: isDay }]">Jour</span>
          <AppToggleSwitch :model-value="!isDay" @update:model-value="store.toggleHeatMode()" />
          <span :class="['toggle-label', { active: !isDay }]">Nuit</span>
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

.polar-col {
  @apply flex-1 flex flex-col items-center gap-3;
}

.toggle-row {
  @apply flex items-center gap-2;
}

.toggle-label {
  @apply text-xs text-gray-400 font-medium transition-colors;
}

.toggle-label.active {
  @apply text-gray-800;
}

.spider-wrapper {
  @apply relative flex items-center justify-center w-full aspect-square max-w-56 max-h-56 flex-1;
}
</style>
