<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardLcz } from "@/types/dashboard"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const bubbles = computed(() => {
  const otherVeg = Math.max(props.data.totalVegetationRate - props.data.treeCoverRate, 0)
  return [
    { id: "trees", label: "Couvert arboré", value: props.data.treeCoverRate, color: "#025400" },
    { id: "otherVeg", label: "Autre végétation", value: otherVeg, color: "#55B250" },
    { id: "water", label: "Surface en eau", value: props.data.waterRate, color: "#3B82F6" }
  ]
})

function formatPct(v: number): string {
  return `${v.toFixed(1)}%`
}

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

  const data = bubbles.value.filter((b) => b.value > 0)
  if (data.length === 0) return

  const root = d3
    .hierarchy({ children: data } as { children: typeof data })
    .sum((d) => (d as unknown as (typeof data)[0]).value || 0)

  d3.pack<{ children: typeof data }>().size([width, height]).padding(4)(
    root as d3.HierarchyNode<{ children: typeof data }>
  )

  const leaves = (root as d3.HierarchyCircularNode<unknown>).leaves() as d3.HierarchyCircularNode<
    (typeof data)[0]
  >[]

  const g = svg.append("g")

  const groups = g
    .selectAll(".bubble")
    .data(leaves)
    .join("g")
    .attr("class", "bubble")
    .attr("transform", (d) => `translate(${d.x},${d.y})`)

  groups
    .append("circle")
    .attr("r", animate ? 0 : (d) => d.r)
    .attr("fill", (d) => d.data.color)
    .attr("opacity", 0.75)
    .attr("stroke", (d) => d.data.color)
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.4)

  if (animate) {
    groups
      .selectAll("circle")
      .transition()
      .duration(600)
      .delay((_, i) => i * 100)
      .ease(d3.easeBackOut.overshoot(0.3))
      .attr("r", (d) => (d as d3.HierarchyCircularNode<(typeof data)[0]>).r)
  }

  groups
    .filter((d) => d.r > 22)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("dy", "-0.5em")
    .attr("font-size", (d) => `${Math.min(d.r / 3, 13)}px`)
    .attr("font-weight", "700")
    .attr("fill", "#fff")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => formatPct(d.data.value))

  groups
    .filter((d) => d.r > 22)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("dy", "0.8em")
    .attr("font-size", (d) => `${Math.min(d.r / 4.5, 10)}px`)
    .attr("fill", "rgba(255,255,255,0.8)")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => d.data.label)

  if (animate) {
    groups.selectAll("text").transition().delay(600).duration(300).attr("opacity", 1)
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
watch(bubbles, () => render(true))
</script>

<template>
  <DashboardWidgetCard subtitle="Couverture végétale et hydrique" title="Végétation et eau">
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
  @apply flex items-center justify-center w-full;
}

.chart-container {
  @apply w-full;
  height: 180px;
}
</style>
