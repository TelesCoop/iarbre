<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import { PLANTABILITY_COLOR_MAP, getPlantabilityScore } from "@/utils/plantability"

interface DistributionEntry {
  score: number
  count: number
}

interface PlantabilityDistributionChartProps {
  entries: DistributionEntry[]
  title?: string
  showLegend?: boolean
}

const props = withDefaults(defineProps<PlantabilityDistributionChartProps>(), {
  title: "Distribution des scores de plantabilité sur la zone.",
  showLegend: true
})

const svgRef = ref<SVGSVGElement | null>(null)
const chartRef = ref<HTMLDivElement | null>(null)
let resizeObserver: ResizeObserver | null = null

const tooltip = ref<{
  visible: boolean
  x: number
  y: number
  label: string
  count: number
  pct: number
}>({
  visible: false,
  x: 0,
  y: 0,
  label: "",
  count: 0,
  pct: 0
})

const bars = computed(() => {
  if (!props.entries || props.entries.length === 0) return []
  const sorted = [...props.entries].sort((a, b) => a.score - b.score)
  const total = sorted.reduce((acc, e) => acc + e.count, 0)
  return sorted.map((entry) => {
    const colorIndex = PLANTABILITY_COLOR_MAP.indexOf(entry.score)
    const color =
      colorIndex !== -1 && colorIndex + 1 < PLANTABILITY_COLOR_MAP.length
        ? String(PLANTABILITY_COLOR_MAP[colorIndex + 1])
        : "#C4C4C4"
    return {
      label: String(entry.score),
      value: entry.count,
      color,
      pct: total > 0 ? entry.count / total : 0
    }
  })
})

function render(animate = false) {
  if (!svgRef.value || bars.value.length === 0) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const rect = svgRef.value.getBoundingClientRect()
  const width = rect.width
  const height = rect.height
  if (width === 0 || height === 0) return

  const barH = Math.min(height * 0.55, 32)
  const labelY = barH + 14
  const gap = 1.5

  const g = svg.append("g")

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
    .attr("y", 0)
    .attr("height", barH)
    .attr("rx", 4)
    .attr("fill", (d) => d.color)
    .attr("opacity", 0.85)
    .attr("width", animate ? 0 : (d) => d.w)
    .on("mouseenter", function (event, d) {
      d3.select(this).attr("opacity", 1)
      if (!chartRef.value) return
      const chartRect = chartRef.value.getBoundingClientRect()
      const mouseRect = event as MouseEvent
      tooltip.value = {
        visible: true,
        x: mouseRect.clientX - chartRect.left,
        y: mouseRect.clientY - chartRect.top - 8,
        label: getPlantabilityScore(Number(d.label)),
        count: d.value,
        pct: d.pct
      }
    })
    .on("mousemove", function (event) {
      if (!chartRef.value) return
      const chartRect = chartRef.value.getBoundingClientRect()
      tooltip.value.x = (event as MouseEvent).clientX - chartRect.left
      tooltip.value.y = (event as MouseEvent).clientY - chartRect.top - 8
    })
    .on("mouseleave", function () {
      d3.select(this).attr("opacity", 0.85)
      tooltip.value.visible = false
    })

  if (animate) {
    g.selectAll(".marimekko-seg")
      .transition()
      .duration(700)
      .delay((_, i) => i * 50)
      .ease(d3.easeCubicOut)
      .attr("width", (d) => (d as (typeof segments)[0]).w)
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

  g.selectAll(".seg-pct")
    .data(segments.filter((s) => s.pct >= 0.06))
    .join("text")
    .attr("class", "seg-pct")
    .attr("x", (d) => d.x + d.w / 2)
    .attr("y", barH / 2)
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("font-size", "9px")
    .attr("font-weight", "600")
    .attr("fill", "#fff")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => `${(d.pct * 100).toFixed(0)}%`)

  if (animate) {
    g.selectAll(".seg-pct").transition().delay(700).duration(300).attr("opacity", 1)
  }
}

onMounted(() => {
  render(true)
  if (svgRef.value?.parentElement) {
    resizeObserver = new ResizeObserver(() => render())
    resizeObserver.observe(svgRef.value.parentElement)
  }
})

onUnmounted(() => resizeObserver?.disconnect())
watch(bars, () => render(true))
</script>

<template>
  <div v-if="bars.length > 0" ref="chartRef" class="distribution-chart">
    <p v-if="title" class="chart-title">{{ title }}</p>
    <svg ref="svgRef" class="chart-svg" />
    <div
      v-if="tooltip.visible"
      class="chart-tooltip"
      :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
    >
      <span class="tooltip-label">{{ tooltip.label }}</span>
      <span class="tooltip-detail"
        >{{ tooltip.count }} tuiles · {{ (tooltip.pct * 100).toFixed(1) }}%</span
      >
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.distribution-chart {
  @apply px-4 py-3 relative;
}

.chart-title {
  @apply text-xs font-semibold text-gray-700 mb-3;
}

.chart-svg {
  @apply w-full;
  height: 56px;
}

.chart-tooltip {
  @apply absolute z-10 pointer-events-none;
  @apply bg-gray-800 text-white rounded-md px-3 py-2 shadow-md;
  @apply flex flex-col gap-0.5;
  transform: translate(-50%, -100%);
}

.tooltip-label {
  @apply text-xs font-medium;
}

.tooltip-detail {
  @apply text-xs text-gray-300;
}
</style>
