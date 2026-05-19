<script lang="ts" setup>
import { computed } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardVegetation } from "@/types/dashboard"
import { VEGETATION_COLORS } from "@/utils/dashboardColors"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"

interface Props {
  data: DashboardVegetation
}

const props = defineProps<Props>()

const m2ToKm2 = (m2: number) => m2 / 1_000_000

const hasData = computed(() => props.data.totalm2 >= 1)

const totalDisplay = computed(
  () => `${m2ToKm2(props.data.totalm2).toLocaleString("fr-FR", { maximumFractionDigits: 2 })} km²`
)

const items = computed(() => [
  { label: "TOTALE", value: m2ToKm2(props.data.totalm2), color: "#426a45" },
  { label: "HAUTE", value: m2ToKm2(props.data.treesSurfaceM2), color: VEGETATION_COLORS.trees },
  { label: "MOYENNE", value: m2ToKm2(props.data.bushesSurfaceM2), color: VEGETATION_COLORS.bushes },
  { label: "BASSE", value: m2ToKm2(props.data.grassSurfaceM2), color: VEGETATION_COLORS.grass }
])

function formatKm2(km2: number): string {
  return `${km2.toLocaleString("fr-FR", { maximumFractionDigits: 2 })} km²`
}

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const data = items.value
    const maxVal = d3.max(data, (d) => d.value) || 1

    const margin = { top: 32, right: 12, bottom: 24, left: 12 }
    const innerW = width - margin.left - margin.right
    const innerH = height - margin.top - margin.bottom
    if (innerH <= 0) return

    const xScale = d3
      .scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, innerW])
      .padding(0.5)

    const yScale = d3
      .scaleLinear()
      .domain([0, maxVal * 1.3])
      .range([innerH, 0])

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    const cx = (d: (typeof data)[0]) => xScale(d.label)! + xScale.bandwidth() / 2

    g.selectAll(".stem")
      .data(data)
      .join("line")
      .attr("class", "stem")
      .attr("x1", (d) => cx(d))
      .attr("x2", (d) => cx(d))
      .attr("y1", innerH)
      .attr("y2", animate ? innerH : (d) => yScale(d.value))
      .attr("stroke", (d) => d.color)
      .attr("stroke-width", 2.5)
      .attr("stroke-linecap", "round")

    if (animate) {
      g.selectAll<SVGLineElement, (typeof data)[0]>(".stem")
        .transition()
        .duration(700)
        .ease(d3.easeCubicOut)
        .attr("y2", (d) => yScale(d.value))
    }

    const dotR = 18

    const dots = g
      .selectAll(".dot")
      .data(data)
      .join("circle")
      .attr("class", "dot")
      .attr("cx", (d) => cx(d))
      .attr("cy", animate ? innerH : (d) => yScale(d.value))
      .attr("r", dotR)
      .attr("fill", (d) => d.color)

    if (animate) {
      dots
        .transition()
        .duration(700)
        .ease(d3.easeCubicOut)
        .attr("cy", (d) => yScale(d.value))
    }

    const valLabels = g
      .selectAll(".dot-val")
      .data(data)
      .join("text")
      .attr("class", "dot-val")
      .attr("x", (d) => cx(d))
      .attr("y", animate ? innerH : (d) => yScale(d.value))
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", "9px")
      .attr("font-weight", "bold")
      .attr("fill", "white")
      .attr("opacity", animate ? 0 : 1)
      .text((d) => `${d.value.toLocaleString("fr-FR", { maximumFractionDigits: 2 })}`)

    if (animate) {
      valLabels
        .transition()
        .delay(500)
        .duration(300)
        .attr("y", (d) => yScale(d.value))
        .attr("opacity", 1)
    }

    const haLabels = g
      .selectAll(".ha-label")
      .data(data)
      .join("text")
      .attr("class", "ha-label")
      .attr("x", (d) => cx(d))
      .attr("y", animate ? innerH : (d) => yScale(d.value) - dotR - 5)
      .attr("text-anchor", "middle")
      .attr("font-size", "9px")
      .attr("font-weight", "600")
      .attr("fill", "#374151")
      .attr("opacity", animate ? 0 : 1)
      .text((d) => formatKm2(d.value))

    if (animate) {
      haLabels
        .transition()
        .delay(600)
        .duration(300)
        .attr("y", (d) => yScale(d.value) - dotR - 5)
        .attr("opacity", 1)
    }

    g.selectAll(".x-label")
      .data(data)
      .join("text")
      .attr("class", "x-label")
      .attr("x", (d) => cx(d))
      .attr("y", innerH + 16)
      .attr("text-anchor", "middle")
      .attr("font-size", "9px")
      .attr("fill", "#9CA3AF")
      .text((d) => d.label)
  },
  [items]
)
</script>

<template>
  <DashboardWidgetCard
    :subtitle="`Distribution de la végétation par strates`"
    title="Végétation existante"
  >
    <div v-if="hasData" class="widget-body">
      <svg ref="svgRef" width="100%" height="100%" />
    </div>
    <div v-else class="widget-empty">
      <span class="empty-text">Données indisponibles</span>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 w-full min-h-[200px];
}

.widget-empty {
  @apply flex-1 flex items-center justify-center;
}

.empty-text {
  @apply text-sm text-gray-400;
}
</style>
