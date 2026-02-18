<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardLcz } from "@/types/dashboard"
import { SURFACE_COLORS } from "@/utils/dashboardColors"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const bars = computed(() => {
  const raw = [
    {
      label: "Végétation",
      value: props.data.totalVegetationRate,
      color: SURFACE_COLORS.vegetation
    },
    {
      label: "Imperméable",
      value: props.data.impermeableSurfaceRate,
      color: SURFACE_COLORS.impermeable
    },
    { label: "Bâti", value: props.data.buildingRate, color: SURFACE_COLORS.building },
    {
      label: "Sol perméable",
      value: props.data.permeableSoilRate,
      color: SURFACE_COLORS.permeableSoil
    },
    { label: "Eau", value: props.data.waterRate, color: SURFACE_COLORS.water }
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

  const marginTop = 20
  const marginBottom = 40
  const labelFontSize = Math.min(Math.max(width / data.length / 8, 8), 11)
  const valueFontSize = Math.min(Math.max(width / data.length / 7, 9), 12)
  const chartH = height - marginTop - marginBottom
  const barGap = Math.min(width * 0.03, 12)
  const barW = Math.min((width - barGap * (data.length - 1)) / data.length, 48)
  const totalW = data.length * barW + (data.length - 1) * barGap
  const offsetX = (width - totalW) / 2

  const maxValue = d3.max(data, (d) => d.value) || 1

  const yScale = d3.scaleLinear().domain([0, maxValue]).range([0, chartH])

  const g = svg.append("g").attr("transform", `translate(${offsetX},${marginTop})`)

  const cols = g
    .selectAll(".bar-col")
    .data(data)
    .join("g")
    .attr("class", "bar-col")
    .attr("transform", (_, i) => `translate(${i * (barW + barGap)},0)`)

  cols
    .append("rect")
    .attr("x", 0)
    .attr("width", barW)
    .attr("rx", 4)
    .attr("fill", (d) => d.color)
    .attr("opacity", 0.8)
    .attr("y", animate ? chartH : (d) => chartH - yScale(d.value))
    .attr("height", animate ? 0 : (d) => yScale(d.value))

  cols
    .append("text")
    .attr("x", barW / 2)
    .attr("y", (d) => (animate ? chartH - 6 : chartH - yScale(d.value) - 6))
    .attr("text-anchor", "middle")
    .attr("font-size", `${valueFontSize}px`)
    .attr("font-weight", "700")
    .attr("fill", (d) => d.color)
    .attr("opacity", animate ? 0 : 1)
    .text((d) => `${d.value.toFixed(1)}%`)

  cols
    .append("text")
    .attr("x", barW / 2)
    .attr("y", chartH + 16)
    .attr("text-anchor", "middle")
    .attr("font-size", `${labelFontSize}px`)
    .attr("fill", "#6B7280")
    .text((d) => d.label)

  if (animate) {
    cols
      .selectAll("rect")
      .transition()
      .duration(700)
      .delay((_, i) => i * 80)
      .ease(d3.easeCubicOut)
      .attr("y", (d) => chartH - yScale((d as (typeof data)[0]).value))
      .attr("height", (d) => yScale((d as (typeof data)[0]).value))

    cols
      .selectAll("text:first-of-type")
      .transition()
      .duration(400)
      .delay((_, i) => 300 + i * 80)
      .attr("opacity", 1)
      .attr("y", (d) => chartH - yScale((d as (typeof data)[0]).value) - 6)
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
      <svg ref="svgRef" height="100%" width="100%" />
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex items-center justify-center w-full;
}
</style>
