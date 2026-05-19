<script lang="ts" setup>
import { computed } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardLcz } from "@/types/dashboard"
import { SURFACE_COLORS } from "@/utils/dashboardColors"
import { useD3Chart, type D3ChartContext } from "@/composables/useD3Chart"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const slices = computed(() => {
  const impermeableVal =
    Math.round(((props.data.buildingRate ?? 0) + (props.data.impermeableSurfaceRate ?? 0)) * 10) /
    10
  return [
    { label: "Imperméable", value: impermeableVal, color: SURFACE_COLORS.impermeable },
    {
      label: "Perméable",
      value: props.data.permeableSoilRate ?? 0,
      color: SURFACE_COLORS.permeableSoil
    },
    {
      label: "Végétation",
      value: props.data.totalVegetationRate ?? 0,
      color: SURFACE_COLORS.vegetation
    },
    { label: "Eau", value: props.data.waterRate ?? 0, color: SURFACE_COLORS.water }
  ].filter((s) => s.value > 0)
})

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const legendH = 52
    const chartH = height - legendH
    const radius = Math.min(width, chartH) / 2
    if (radius <= 0) return

    const cx = width / 2
    const cy = chartH / 2

    const pie = d3
      .pie<(typeof slices.value)[0]>()
      .value((d) => d.value)
      .sort(null)
    const arcGen = d3
      .arc<d3.PieArcDatum<(typeof slices.value)[0]>>()
      .innerRadius(radius * 0.55)
      .outerRadius(radius)
      .cornerRadius(3)
      .padAngle(0.025)

    const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)
    const arcs = pie(slices.value)

    g.selectAll(".donut-slice")
      .data(arcs)
      .join("path")
      .attr("class", "donut-slice")
      .attr("fill", (d) => d.data.color)
      .attr("opacity", 0.85)
      .attr("d", animate ? (d) => arcGen({ ...d, endAngle: d.startAngle })! : (d) => arcGen(d)!)
      .on("mouseenter", function () {
        d3.select(this).attr("opacity", 1)
      })
      .on("mouseleave", function () {
        d3.select(this).attr("opacity", 0.85)
      })

    if (animate) {
      g.selectAll<SVGPathElement, d3.PieArcDatum<(typeof slices.value)[0]>>(".donut-slice")
        .transition()
        .duration(700)
        .delay((_, i) => i * 80)
        .ease(d3.easeCubicOut)
        .attrTween("d", function (d) {
          const interp = d3.interpolate(d.startAngle, d.endAngle)
          return (t) => arcGen({ ...d, endAngle: interp(t) })!
        })
    }

    const legendY = chartH + legendH / 2
    const itemW = width / slices.value.length

    slices.value.forEach((item, i) => {
      const x = itemW * i + 8
      svg
        .append("circle")
        .attr("cx", x)
        .attr("cy", legendY - 8)
        .attr("r", 4)
        .attr("fill", item.color)
      svg
        .append("text")
        .attr("x", x + 10)
        .attr("y", legendY - 8)
        .attr("dominant-baseline", "central")
        .attr("font-size", "9px")
        .attr("fill", "#374151")
        .text(item.label)
      svg
        .append("text")
        .attr("x", x + 10)
        .attr("y", legendY + 8)
        .attr("dominant-baseline", "central")
        .attr("font-size", "9px")
        .attr("font-weight", "600")
        .attr("fill", "#6B7280")
        .text(`${item.value.toFixed(1)}%`)
    })
  },
  [slices]
)
</script>

<template>
  <DashboardWidgetCard
    subtitle="Répartition du territoire"
    title="Types de surface (étude ZCL du CEREMA 2023)"
  >
    <div class="widget-body">
      <svg ref="svgRef" width="100%" height="100%" />
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 w-full min-h-[200px];
}
</style>
