<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import type { DashboardPlantability } from "@/types/dashboard"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"

const PLANTABILITY_MAX_SCORE = 10

interface Props {
  data: DashboardPlantability
}

const props = defineProps<Props>()

const score = computed(() => Math.round(props.data.averageNormalizedIndice * 10) / 10)
const arcColor = computed(() => {
  const idx = PLANTABILITY_COLOR_MAP.indexOf(Math.round(score.value))
  if (idx !== -1 && idx + 1 < PLANTABILITY_COLOR_MAP.length) {
    return String(PLANTABILITY_COLOR_MAP[idx + 1])
  }
  return "#426A45"
})

const getColorForScore = (scoreValue: number): string => {
  const idx = PLANTABILITY_COLOR_MAP.indexOf(scoreValue)
  if (idx !== -1 && idx + 1 < PLANTABILITY_COLOR_MAP.length) {
    return String(PLANTABILITY_COLOR_MAP[idx + 1])
  }
  return "#C4C4C4"
}

const svgRef = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

const bars = computed(() => {
  const distribution = props.data.distribution
  const entries = Object.keys(distribution)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => ({
      label: k,
      value: distribution[k],
      color: getColorForScore(Number(k))
    }))
  const total = entries.reduce((a, b) => a + b.value, 0)
  return entries.map((e) => ({ ...e, pct: total > 0 ? e.value / total : 0 }))
})

function render(animate = false) {
  if (!svgRef.value) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const rect = svgRef.value.getBoundingClientRect()
  const width = rect.width
  const height = rect.height
  if (width === 0 || height === 0) return

  const barH = Math.min(height * 0.5, 32)
  const chartTotalH = barH + 14 + 10
  const offsetY = Math.max((height - chartTotalH) / 2, 0)
  const barY = 0
  const labelY = barY + barH + 14
  const gap = 1.5

  const g = svg.append("g").attr("transform", `translate(0,${offsetY})`)

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
    .attr("y", barY)
    .attr("height", barH)
    .attr("rx", 4)
    .attr("fill", (d) => d.color)
    .attr("opacity", 0.85)
    .attr("width", animate ? 0 : (d) => d.w)
    .on("mouseenter", function () {
      d3.select(this).attr("opacity", 1)
    })
    .on("mouseleave", function () {
      d3.select(this).attr("opacity", 0.85)
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
    .attr("y", barY + barH / 2)
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
  <DashboardWidgetCard subtitle="Indice moyen de plantabilité" title="Plantabilité">
    <div class="widget-body">
      <DashboardArcScore
        :color="arcColor"
        :max-value="PLANTABILITY_MAX_SCORE"
        :value="score"
        label="plantabilité"
      />
      <div class="chart-container">
        <svg ref="svgRef" width="100%" height="100%" />
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex flex-col items-center justify-center gap-4 w-full;
}

.chart-container {
  @apply flex-1 w-full;
  min-height: 40px;
}
</style>
