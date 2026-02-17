<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"

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
let resizeObserver: ResizeObserver | null = null

const segments = computed(() => {
  if (!props.entries || props.entries.length === 0) return []
  return [...props.entries]
    .sort((a, b) => a.score - b.score)
    .map((entry) => {
      const colorIndex = PLANTABILITY_COLOR_MAP.indexOf(entry.score)
      const color =
        colorIndex !== -1 && colorIndex + 1 < PLANTABILITY_COLOR_MAP.length
          ? String(PLANTABILITY_COLOR_MAP[colorIndex + 1])
          : "#C4C4C4"
      return { label: `${entry.score}/10`, value: entry.count, color }
    })
})

function render(animate = false) {
  if (!svgRef.value || segments.value.length === 0) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const rect = svgRef.value.getBoundingClientRect()
  const width = rect.width
  const height = rect.height
  if (width === 0 || height === 0) return

  const legendH = props.showLegend ? 32 : 0
  const titleH = props.title ? 24 : 0
  const chartH = height - legendH - titleH
  const size = Math.min(width, chartH)
  const cx = width / 2
  const cy = titleH + chartH / 2
  const outerR = size / 2 - 4
  const innerR = 0

  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

  if (props.title) {
    svg
      .append("text")
      .attr("x", cx)
      .attr("y", 16)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", "600")
      .attr("fill", "#374151")
      .text(props.title)
  }

  const pie = d3
    .pie<(typeof segments.value)[0]>()
    .value((d) => d.value)
    .sort(null)
    .padAngle(0.02)

  const arc = d3
    .arc<d3.PieArcDatum<(typeof segments.value)[0]>>()
    .innerRadius(innerR)
    .outerRadius(outerR)

  const zeroArc = d3
    .arc<d3.PieArcDatum<(typeof segments.value)[0]>>()
    .innerRadius(innerR)
    .outerRadius(0)

  const paths = g
    .selectAll("path")
    .data(pie(segments.value))
    .join("path")
    .attr("d", animate ? (zeroArc as never) : (arc as never))
    .attr("fill", (d) => d.data.color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)

  if (animate) {
    paths
      .transition()
      .duration(600)
      .ease(d3.easeCubicOut)
      .attrTween("d", function (d) {
        const interp = d3.interpolate({ startAngle: d.startAngle, endAngle: d.startAngle }, d)
        return function (t) {
          return arc(interp(t))!
        }
      })
  }

  if (props.showLegend) {
    const legendY = height - legendH / 2
    const itemW = 50
    const totalW = segments.value.length * itemW
    const startX = (width - totalW) / 2

    segments.value.forEach((seg, i) => {
      const x = startX + i * itemW + itemW / 2
      svg
        .append("rect")
        .attr("x", x - 16)
        .attr("y", legendY - 5)
        .attr("width", 10)
        .attr("height", 10)
        .attr("rx", 2)
        .attr("fill", seg.color)

      svg
        .append("text")
        .attr("x", x - 2)
        .attr("y", legendY + 4)
        .attr("font-size", "10px")
        .attr("fill", "#6B7280")
        .text(seg.label)
    })
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
watch(segments, () => render(true))
</script>

<template>
  <div v-if="segments.length > 0" class="p-4">
    <svg ref="svgRef" class="w-full h-64" />
  </div>
</template>
