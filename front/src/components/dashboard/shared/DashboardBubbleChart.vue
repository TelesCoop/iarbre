<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import type { BubbleItem } from "@/types/dashboard"

interface Props {
  bubbles: BubbleItem[]
  formatter: (value: number) => string
}

const props = defineProps<Props>()

const filteredBubbles = computed(() => props.bubbles.filter((b) => b.value > 0))

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

  const data = filteredBubbles.value
  if (data.length === 0) return

  const root = d3
    .hierarchy({ children: data } as { children: typeof data })
    .sum((d) => (d as unknown as (typeof data)[0]).value || 0)

  const legendH = 48
  const chartH = height - legendH
  const chartSize = Math.min(width, chartH)
  const offsetX = (width - chartSize) / 2
  const offsetY = (chartH - chartSize) / 2

  d3.pack<{ children: typeof data }>().size([chartSize, chartSize]).padding(8)(
    root as d3.HierarchyNode<{ children: typeof data }>
  )

  const leaves = (root as d3.HierarchyCircularNode<unknown>).leaves() as d3.HierarchyCircularNode<
    (typeof data)[0]
  >[]

  const g = svg.append("g").attr("transform", `translate(${offsetX},${offsetY})`)

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
    .attr("opacity", 0.9)
    .attr("stroke", (d) => d.data.color)
    .attr("stroke-width", 2)
    .attr("stroke-opacity", 0.5)

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
    .filter((d) => d.r > 20)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("dy", "-0.4em")
    .attr("font-size", (d) => `${Math.min(d.r / 3, 14)}px`)
    .attr("font-weight", "700")
    .attr("fill", "#fff")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => props.formatter(d.data.value))

  groups
    .filter((d) => d.r > 28)
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("dy", "0.9em")
    .attr("font-size", (d) => `${Math.min(d.r / 4, 11)}px`)
    .attr("fill", "rgba(255,255,255,0.85)")
    .attr("opacity", animate ? 0 : 1)
    .text((d) => d.data.label)

  if (animate) {
    groups.selectAll("text").transition().delay(600).duration(300).attr("opacity", 1)
  }

  const legendY = chartH + legendH / 2
  const itemW = width / data.length
  const legendFontSize = Math.min(Math.max(itemW / 10, 9), 13)
  const showValue = itemW > 100

  data.forEach((item, i) => {
    const x = itemW * i + itemW / 2
    svg
      .append("circle")
      .attr("cx", x - 28)
      .attr("cy", legendY)
      .attr("r", 4)
      .attr("fill", item.color)
    svg
      .append("text")
      .attr("x", x - 18)
      .attr("y", legendY)
      .attr("dominant-baseline", "central")
      .attr("font-size", `${legendFontSize}px`)
      .attr("font-weight", "500")
      .attr("fill", "#374151")
      .text(showValue ? `${item.label} · ${props.formatter(item.value)}` : item.label)
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
watch(filteredBubbles, () => render(true))
</script>

<template>
  <svg ref="svgRef" height="100%" width="100%" />
</template>
