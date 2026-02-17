<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardVegetation } from "@/types/dashboard"

interface Props {
  data: DashboardVegetation
}

const props = defineProps<Props>()

const hasData = computed(() => props.data.totalHa >= 1)

const totalDisplay = computed(() => {
  const ha = props.data.totalHa
  if (ha >= 1000) return `${(ha / 1000).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
})

const bubbles = computed(() => [
  { id: "trees", label: "Arborée", value: props.data.treesSurfaceHa, color: "#025400" },
  { id: "bushes", label: "Arbustive", value: props.data.bushesSurfaceHa, color: "#55B250" },
  { id: "grass", label: "Herbacée", value: props.data.grassSurfaceHa, color: "#A6CC4A" }
])

function formatHa(ha: number): string {
  if (ha >= 1000) return `${(ha / 1000).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
}

const svgRef = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

function render(animate = false) {
  if (!svgRef.value || !hasData.value) return
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

  d3.pack<{ children: typeof data }>().size([width, height]).padding(6)(
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
    .attr("opacity", 0.8)
    .attr("stroke", (d) => d.data.color)
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.3)

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
    .filter((d) => d.r > 24)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("dy", "-0.5em")
    .attr("font-size", (d) => `${Math.min(d.r / 3.5, 13)}px`)
    .attr("font-weight", "700")
    .attr("fill", "#fff")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => formatHa(d.data.value))

  groups
    .filter((d) => d.r > 24)
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
  <DashboardWidgetCard subtitle="Surfaces de végétation par strate" title="Végétation existante">
    <div v-if="hasData" class="widget-body">
      <div class="total-display">
        <span class="total-value">{{ totalDisplay }}</span>
        <span class="total-label">de végétation totale</span>
      </div>
      <div class="chart-container">
        <svg ref="svgRef" height="100%" width="100%" />
      </div>
    </div>
    <div v-else class="widget-empty">
      <span class="empty-text">Données indisponibles</span>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex items-center gap-3 w-full;
}

.total-display {
  @apply flex flex-col items-center;
}

.total-value {
  @apply text-2xl md:text-3xl font-bold text-primary-700;
}

.total-label {
  @apply text-xs text-gray-500;
}

.chart-container {
  @apply w-full;
  height: 150px;
}

.widget-empty {
  @apply flex-1 flex items-center justify-center;
}

.empty-text {
  @apply text-sm text-gray-400;
}
</style>
