<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardLcz } from "@/types/dashboard"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const bars = computed(() => {
  const raw = [
    { label: "Végétation", value: props.data.totalVegetationRate, color: "#55B250" },
    { label: "Imperméable", value: props.data.impermeableSurfaceRate, color: "#6B7280" },
    { label: "Bâti", value: props.data.buildingRate, color: "#F59E0B" },
    { label: "Sol perméable", value: props.data.permeableSoilRate, color: "#D4A853" },
    { label: "Eau", value: props.data.waterRate, color: "#3B82F6" }
  ]
  return raw.filter((b) => b.value > 0).sort((a, b) => b.value - a.value)
})

const svgRef = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

function render(animate = false) {
  if (!svgRef.value) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const rect = svgRef.value.getBoundingClientRect()
  const width = rect.width
  const height = rect.height
  if (width === 0 || height === 0) return

  const data = bars.value
  if (data.length === 0) return

  const marginLeft = 90
  const marginRight = 44
  const marginTop = 4
  const marginBottom = 4
  const barHeight = Math.min((height - marginTop - marginBottom) / data.length - 6, 28)
  const gap = 6

  const maxValue = d3.max(data, (d) => d.value) || 1

  const xScale = d3
    .scaleLinear()
    .domain([0, maxValue])
    .range([0, width - marginLeft - marginRight])

  const g = svg.append("g").attr("transform", `translate(${marginLeft},${marginTop})`)

  const rows = g
    .selectAll(".bar-row")
    .data(data)
    .join("g")
    .attr("class", "bar-row")
    .attr("transform", (_, i) => `translate(0,${i * (barHeight + gap)})`)

  rows
    .append("text")
    .attr("x", -8)
    .attr("y", barHeight / 2)
    .attr("text-anchor", "end")
    .attr("dominant-baseline", "central")
    .attr("font-size", "11px")
    .attr("fill", "#6B7280")
    .text((d) => d.label)

  rows
    .append("rect")
    .attr("y", 0)
    .attr("height", barHeight)
    .attr("rx", 4)
    .attr("fill", (d) => d.color)
    .attr("opacity", 0.8)
    .attr("width", animate ? 0 : (d) => xScale(d.value))

  rows
    .append("text")
    .attr("x", (d) => (animate ? 4 : xScale(d.value) + 6))
    .attr("y", barHeight / 2)
    .attr("dominant-baseline", "central")
    .attr("font-size", "11px")
    .attr("font-weight", "700")
    .attr("fill", (d) => d.color)
    .attr("opacity", animate ? 0 : 1)
    .text((d) => `${d.value.toFixed(1)}%`)

  if (animate) {
    rows
      .selectAll("rect")
      .transition()
      .duration(700)
      .delay((_, i) => i * 80)
      .ease(d3.easeCubicOut)
      .attr("width", (d) => xScale((d as (typeof data)[0]).value))

    rows
      .selectAll("text:last-of-type")
      .transition()
      .duration(400)
      .delay((_, i) => 300 + i * 80)
      .attr("opacity", 1)
      .attr("x", (d) => xScale((d as (typeof data)[0]).value) + 6)
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
  <DashboardWidgetCard subtitle="Répartition par type de surface" title="Surfaces">
    <div class="widget-body">
      <div class="chart-container">
        <svg ref="svgRef" width="100%" height="100%" />
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply w-full;
}

.chart-container {
  @apply w-full;
  height: 200px;
}
</style>
