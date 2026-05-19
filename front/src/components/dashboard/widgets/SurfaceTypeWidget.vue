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
  const permeableVal = Math.round((props.data.permeableSoilRate ?? 0) * 10) / 10
  const autresVal = Math.max(0, Math.round((100 - impermeableVal - permeableVal) * 10) / 10)
  return [
    {
      label: "Surface minérale imperméable",
      value: impermeableVal,
      color: SURFACE_COLORS.impermeable
    },
    { label: "Sol nu perméable", value: permeableVal, color: SURFACE_COLORS.permeableSoil },
    { label: "Autres surfaces", value: autresVal, color: SURFACE_COLORS.vegetation }
  ].filter((s) => s.value > 0)
})

const primaryVal = computed(() => slices.value[0]?.value ?? 0)

const { svgRef } = useD3Chart(
  ({ svg, width, height }: D3ChartContext, animate: boolean) => {
    const radius = Math.min(width, height) / 2
    if (radius <= 0) return

    const cx = width / 2
    const cy = height / 2

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
      <div class="donut-wrapper">
        <svg ref="svgRef" width="100%" height="100%" />
        <div class="donut-center">
          <span class="donut-val">{{ primaryVal.toFixed(1) }}%</span>
        </div>
      </div>
      <div class="legend">
        <div v-for="s in slices" :key="s.label" class="legend-item">
          <span class="legend-dot" :style="{ backgroundColor: s.color }" />
          <div class="legend-text">
            <span class="legend-label">{{ s.label }}</span>
            <span class="legend-value">{{ s.value.toFixed(1) }} %</span>
          </div>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-row items-center gap-6;
}

.donut-wrapper {
  @apply relative flex items-center justify-center shrink-0;
  width: 160px;
  height: 160px;
}

.donut-center {
  @apply absolute inset-0 flex flex-col items-center justify-center pointer-events-none;
}

.donut-val {
  @apply text-base font-bold text-gray-800;
}

.legend {
  @apply flex flex-col gap-4 flex-1;
}

.legend-item {
  @apply flex items-start gap-2;
}

.legend-dot {
  @apply w-2.5 h-2.5 rounded-full shrink-0 mt-0.5;
}

.legend-text {
  @apply flex flex-col;
}

.legend-label {
  @apply text-xs text-gray-500;
}

.legend-value {
  @apply text-sm font-semibold text-gray-800 tabular-nums;
}
</style>
