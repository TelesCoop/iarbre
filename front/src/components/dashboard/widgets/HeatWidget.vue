<script lang="ts" setup>
import { computed, ref } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"
import type { DashboardVulnerability } from "@/types/dashboard"
import { useDashboardStore } from "@/stores/dashboard"
import { HEAT_COLORS } from "@/utils/dashboardColors"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"

const VULNERABILITY_MAX_SCORE = 9
const POLAR_MAX_SCORE = 3

interface Props {
  data: DashboardVulnerability
}

const props = defineProps<Props>()
const store = useDashboardStore()

const isDay = computed(() => store.heatMode === "day")
const currentScore = computed(() => (isDay.value ? props.data.averageDay : props.data.averageNight))
const palette = computed(() => (isDay.value ? HEAT_COLORS.day : HEAT_COLORS.night))

const axes = computed(() => {
  const expo = isDay.value ? props.data.expoDay : props.data.expoNight
  const sensibility = isDay.value ? props.data.sensibilityDay : props.data.sensibilityNight
  const capaf = isDay.value ? props.data.capafDay : props.data.capafNight
  return [
    { label: "Exposition", value: expo, color: palette.value.expo },
    { label: "Sensibilité", value: sensibility, color: palette.value.sensibility },
    { label: "Cap. adapt.", value: capaf, color: palette.value.capaf }
  ]
})

const scoreText = computed(() => {
  const rounded = Math.round(currentScore.value * 10) / 10
  return `${rounded.toFixed(1)}/${VULNERABILITY_MAX_SCORE}`
})

const currentRatios = ref([0, 0, 0])
const hoveredAxis = ref<{ label: string; value: number; color: string; level: string } | null>(null)
const tooltipPos = ref({ x: 0, y: 0 })

function getLevel(value: number): string {
  if (value < 1) return "Faible"
  if (value < 2) return "Modéré"
  return "Élevé"
}

function labelAnchor(angle: number): string {
  const a = ((angle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)
  if (a > 0.4 && a < Math.PI - 0.4) return "start"
  if (a > Math.PI + 0.4 && a < 2 * Math.PI - 0.4) return "end"
  return "middle"
}

function labelDy(angle: number): string {
  const a = ((angle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)
  if (a < 0.4 || a > 2 * Math.PI - 0.4) return "0.85em"
  if (a > Math.PI - 0.4 && a < Math.PI + 0.4) return "-0.35em"
  return "0.35em"
}

function updateTooltipPos(event: MouseEvent, svgEl: SVGSVGElement) {
  const wrapperRect = svgEl.closest(".arc-wrapper")?.getBoundingClientRect()
  if (!wrapperRect) return
  tooltipPos.value = {
    x: event.clientX - wrapperRect.left,
    y: event.clientY - wrapperRect.top - 44
  }
}

const { svgRef } = useD3Chart(({ svg, width, height }: D3ChartContext, animate: boolean) => {
  const size = Math.min(width, height)
  if (size <= 0) return

  const cx = width / 2
  const cy = height / 2
  const outerR = size / 2 - 28
  const innerR = outerR * 0.66
  const sectorGap = 0.08
  const sectorAngle = (2 * Math.PI) / 3

  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

  const bgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(innerR)
    .outerRadius(outerR)

  const fgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(innerR)
    .outerRadius(outerR)
    .cornerRadius(3)

  const hitArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(innerR - 6)
    .outerRadius(outerR + 6)

  axes.value.forEach((axis, i) => {
    const start = i * sectorAngle + sectorGap / 2
    const end = (i + 1) * sectorAngle - sectorGap / 2
    const sectorSpan = end - start

    g.append("path")
      .attr("d", bgArc({ startAngle: start, endAngle: end })!)
      .attr("fill", "#f3f4f6")

    for (let t = 1; t < POLAR_MAX_SCORE; t++) {
      const tickAngle = start + (t / POLAR_MAX_SCORE) * sectorSpan
      const dotR = innerR - 3
      g.append("circle")
        .attr("cx", dotR * Math.sin(tickAngle))
        .attr("cy", -dotR * Math.cos(tickAngle))
        .attr("r", 1.2)
        .attr("fill", "#d1d5db")
    }

    const ratio = Math.min(Math.max(axis.value / POLAR_MAX_SCORE, 0), 1)
    const targetEnd = start + ratio * sectorSpan
    const startFrom = animate ? start + currentRatios.value[i] * sectorSpan : targetEnd

    const sectorG = g.append("g").attr("class", "sector-group")

    const path = sectorG
      .append("path")
      .datum({ startAngle: start, endAngle: Math.max(startFrom, start + 0.01) })
      .attr("d", (d) => fgArc(d)!)
      .attr("fill", axis.color)
      .attr("opacity", 0.4)
      .attr("stroke", axis.color)
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.7)

    if (animate && Math.abs(targetEnd - startFrom) > 0.01) {
      path
        .transition()
        .duration(700)
        .ease(d3.easeCubicOut)
        .attrTween("d", function (d) {
          const interp = d3.interpolate(d.endAngle, targetEnd)
          return function (t) {
            d.endAngle = interp(t)
            return fgArc(d)!
          }
        })
    }

    const svgEl = svgRef.value!
    sectorG
      .append("path")
      .attr("d", hitArc({ startAngle: start, endAngle: end })!)
      .attr("fill", "transparent")
      .style("cursor", "pointer")
      .on("mouseenter", function (event: MouseEvent) {
        g.selectAll<SVGGElement, unknown>(".sector-group").each(function () {
          d3.select(this).select("path").transition().duration(150).attr("opacity", 0.15)
        })
        d3.select(this.parentNode as Element)
          .select("path")
          .transition()
          .duration(150)
          .attr("opacity", 0.7)
        hoveredAxis.value = { ...axis, level: getLevel(axis.value) }
        updateTooltipPos(event, svgEl)
      })
      .on("mousemove", (event: MouseEvent) => updateTooltipPos(event, svgEl))
      .on("mouseleave", function () {
        g.selectAll<SVGGElement, unknown>(".sector-group").each(function () {
          d3.select(this).select("path").transition().duration(200).attr("opacity", 0.4)
        })
        hoveredAxis.value = null
      })

    currentRatios.value[i] = ratio

    const midAngle = start + sectorSpan / 2
    const connStartR = outerR + 3
    const connEndR = outerR + 10
    const labelR = outerR + 14
    const anchor = labelAnchor(midAngle)
    const dy = labelDy(midAngle)

    g.append("line")
      .attr("x1", connStartR * Math.sin(midAngle))
      .attr("y1", -connStartR * Math.cos(midAngle))
      .attr("x2", connEndR * Math.sin(midAngle))
      .attr("y2", -connEndR * Math.cos(midAngle))
      .attr("stroke", "#d1d5db")
      .attr("stroke-width", 0.75)

    const lx = labelR * Math.sin(midAngle)
    const ly = -labelR * Math.cos(midAngle)

    const labelG = g.append("g").attr("transform", `translate(${lx},${ly})`)

    labelG
      .append("text")
      .attr("text-anchor", anchor)
      .attr("dominant-baseline", "central")
      .attr("dy", dy)
      .attr("font-size", "9px")
      .attr("fill", "#9CA3AF")
      .text(axis.label)

    const valueDy = parseFloat(dy) + 1.1 + "em"
    labelG
      .append("text")
      .attr("text-anchor", anchor)
      .attr("dominant-baseline", "central")
      .attr("dy", valueDy)
      .attr("font-size", "10px")
      .attr("font-weight", "600")
      .attr("fill", "#374151")
      .text(`${axis.value.toFixed(1)}/${POLAR_MAX_SCORE}`)
  })
}, [axes])
</script>

<template>
  <DashboardWidgetCard subtitle="Vulnérabilité aux températures extrêmes" title="Zones climatiques locales">
    <div class="widget-body">
      <div class="toggle-row">
        <span :class="['toggle-label', { active: isDay }]">Jour</span>
        <AppToggleSwitch :model-value="!isDay" @update:model-value="store.toggleHeatMode()" />
        <span :class="['toggle-label', { active: !isDay }]">Nuit</span>
      </div>

      <div class="arc-wrapper">
        <svg ref="svgRef" width="100%" height="100%" style="overflow: visible" />
        <div class="arc-center">
          <span class="arc-value">{{ scoreText }}</span>
          <span class="arc-label">{{ isDay ? "chaleur jour" : "chaleur nuit" }}</span>
        </div>
        <div
          v-if="hoveredAxis"
          class="chart-tooltip"
          :style="{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y}px` }"
        >
          <span class="tooltip-dot" :style="{ backgroundColor: hoveredAxis.color }" />
          <span class="tooltip-label">{{ hoveredAxis.label }}</span>
          <span class="tooltip-value">{{ hoveredAxis.value.toFixed(1) }}/{{ POLAR_MAX_SCORE }}</span>
          <span class="tooltip-sep">-</span>
          <span class="tooltip-level">{{ hoveredAxis.level }}</span>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex flex-col items-center justify-center gap-2 w-full;
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

.arc-wrapper {
  @apply relative flex items-center justify-center w-full;
  aspect-ratio: 1;
  max-width: 240px;
  max-height: 240px;
  flex: 1 1 0;
}

.arc-center {
  @apply absolute inset-0 flex flex-col items-center justify-center pointer-events-none;
}

.arc-value {
  @apply text-lg font-bold text-gray-800;
}

.arc-label {
  @apply text-xs text-gray-400 leading-tight text-center;
}

.chart-tooltip {
  @apply absolute pointer-events-none flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg shadow-md;
  @apply bg-white border border-gray-100 text-xs whitespace-nowrap;
  transform: translateX(-50%);
  z-index: 10;
}

.tooltip-dot {
  @apply w-2 h-2 rounded-full shrink-0;
}

.tooltip-label {
  @apply text-gray-600 font-medium;
}

.tooltip-value {
  @apply text-gray-800 font-bold tabular-nums;
}

.tooltip-sep {
  @apply text-gray-300;
}

.tooltip-level {
  @apply text-gray-400;
}
</style>
