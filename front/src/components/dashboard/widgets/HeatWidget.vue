<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import AppToggleSwitch from "@/components/shared/AppToggleSwitch.vue"
import type { DashboardVulnerability } from "@/types/dashboard"
import { useDashboardStore } from "@/stores/dashboard"

const VULNERABILITY_MAX_SCORE = 9

interface Props {
  data: DashboardVulnerability
}

const props = defineProps<Props>()
const store = useDashboardStore()

const isDay = computed(() => store.heatMode === "day")
const currentScore = computed(() => (isDay.value ? props.data.averageDay : props.data.averageNight))
const accentColor = computed(() => (isDay.value ? "#F59E0B" : "#6366F1"))

const axes = computed(() => {
  const expo = isDay.value ? props.data.expoDay : props.data.expoNight
  const sensibility = isDay.value ? props.data.sensibilityDay : props.data.sensibilityNight
  const capaf = isDay.value ? props.data.capafDay : props.data.capafNight
  return [
    { label: "Exposition", value: expo, color: isDay.value ? "#FBBF24" : "#818CF8" },
    { label: "Sensibilité", value: sensibility, color: isDay.value ? "#F59E0B" : "#6366F1" },
    { label: "Cap. adapt.", value: capaf, color: isDay.value ? "#D97706" : "#4F46E5" }
  ]
})

const svgRef = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

function render(animate = false) {
  if (!svgRef.value) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const rect = svgRef.value.getBoundingClientRect()
  const size = Math.min(rect.width, rect.height)
  const cx = rect.width / 2
  const cy = rect.height / 2
  if (size <= 0) return

  const radius = size / 2 - 36
  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)
  const angleSlice = (2 * Math.PI) / axes.value.length
  const rScale = d3.scaleLinear().domain([0, VULNERABILITY_MAX_SCORE]).range([0, radius])

  const levels = [3, 6, 9]
  levels.forEach((level) => {
    g.append("circle")
      .attr("r", rScale(level))
      .attr("fill", "none")
      .attr("stroke", "#e5e7eb")
      .attr("stroke-width", 0.5)
      .attr("stroke-dasharray", level < 9 ? "2,3" : "none")

    g.append("text")
      .attr("x", 3)
      .attr("y", -rScale(level) - 2)
      .attr("font-size", "8px")
      .attr("fill", "#D1D5DB")
      .text(String(level))
  })

  axes.value.forEach((_, i) => {
    const angle = angleSlice * i - Math.PI / 2
    g.append("line")
      .attr("x2", radius * Math.cos(angle))
      .attr("y2", radius * Math.sin(angle))
      .attr("stroke", "#e5e7eb")
      .attr("stroke-width", 0.5)
  })

  const arc = d3.arc<{
    startAngle: number
    endAngle: number
    innerRadius: number
    outerRadius: number
  }>()

  const wedges = axes.value.map((axis, i) => ({
    startAngle: angleSlice * i,
    endAngle: angleSlice * (i + 1),
    outerRadius: rScale(axis.value),
    color: axis.color,
    value: axis.value,
    label: axis.label
  }))

  g.selectAll(".polar-wedge")
    .data(wedges)
    .join("path")
    .attr("class", "polar-wedge")
    .attr(
      "d",
      (d) =>
        arc({
          startAngle: d.startAngle,
          endAngle: d.endAngle,
          innerRadius: 0,
          outerRadius: animate ? 0 : d.outerRadius
        })!
    )
    .attr("fill", (d) => d.color)
    .attr("opacity", 0.3)
    .attr("stroke", (d) => d.color)
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.6)

  if (animate) {
    g.selectAll<SVGPathElement, (typeof wedges)[0]>(".polar-wedge")
      .transition()
      .duration(700)
      .ease(d3.easeCubicOut)
      .attrTween("d", function (d) {
        const interp = d3.interpolate(0, d.outerRadius)
        return function (t) {
          return arc({
            startAngle: d.startAngle,
            endAngle: d.endAngle,
            innerRadius: 0,
            outerRadius: interp(t)
          })!
        }
      })
  }

  wedges.forEach((w) => {
    const midAngle = (w.startAngle + w.endAngle) / 2 - Math.PI / 2
    const labelR = radius + 14

    const isTop = Math.abs(midAngle + Math.PI / 2) < 0.3
    const anchor = isTop ? "middle" : midAngle > 0 ? "start" : "end"
    const dy = isTop ? "-0.6em" : "0em"

    const labelG = g
      .append("g")
      .attr("transform", `translate(${labelR * Math.cos(midAngle)},${labelR * Math.sin(midAngle)})`)

    labelG
      .append("text")
      .attr("text-anchor", anchor)
      .attr("dominant-baseline", "central")
      .attr("dy", dy)
      .attr("font-size", "11px")
      .attr("font-weight", "600")
      .attr("fill", "#374151")
      .text(`${w.value.toFixed(1)}`)

    labelG
      .append("text")
      .attr("text-anchor", anchor)
      .attr("dominant-baseline", "central")
      .attr("dy", isTop ? "0.7em" : "1.3em")
      .attr("font-size", "9px")
      .attr("fill", "#9CA3AF")
      .text(w.label)
  })
}

onMounted(() => {
  render(true)
  if (svgRef.value?.parentElement) {
    resizeObserver = new ResizeObserver(() => render())
    resizeObserver.observe(svgRef.value.parentElement)
  }
})

onUnmounted(() => resizeObserver?.disconnect())
watch([axes, accentColor], () => render(true))
</script>

<template>
  <DashboardWidgetCard subtitle="Vulnérabilité aux températures extrêmes" title="Îlots de chaleur">
    <div class="widget-body">
      <div class="toggle-row">
        <span :class="['toggle-label', { active: isDay }]">Jour</span>
        <AppToggleSwitch :model-value="!isDay" @update:model-value="store.toggleHeatMode()" />
        <span :class="['toggle-label', { active: !isDay }]">Nuit</span>
      </div>

      <div class="score-and-polar">
        <DashboardArcScore
          :color="accentColor"
          :label="isDay ? 'chaleur jour' : 'chaleur nuit'"
          :max-value="VULNERABILITY_MAX_SCORE"
          :value="Math.round(currentScore * 10) / 10"
        />

        <div class="chart-container">
          <svg ref="svgRef" width="100%" height="100%" />
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-col items-center gap-3 w-full;
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

.score-and-polar {
  @apply flex items-center gap-4 w-full;
}

.chart-container {
  @apply flex-1;
  height: 180px;
}
</style>
