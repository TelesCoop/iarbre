<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"

interface Props {
  value: number
  maxValue: number
  color: string
  label?: string
  displayValue?: string
  size?: number
}

const props = withDefaults(defineProps<Props>(), {
  label: undefined,
  displayValue: undefined,
  size: 120
})

const svgRef = ref<SVGSVGElement | null>(null)
const currentEndAngle = ref(0)

const targetAngle = computed(() => {
  const ratio = Math.min(Math.max(props.value / props.maxValue, 0), 1)
  return ratio * 2 * Math.PI
})

const centerText = computed(() => {
  if (props.displayValue) return props.displayValue
  return `${props.value.toFixed(1)}/${props.maxValue}`
})

let resizeObs: ResizeObserver | null = null

function render(animate = true) {
  if (!svgRef.value) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const s = props.size
  const cx = s / 2
  const cy = s / 2
  const outerR = s / 2 - 2
  const innerR = outerR * 0.72
  const gap = 0.04

  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

  const bgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(innerR)
    .outerRadius(outerR)

  g.append("path")
    .attr("d", bgArc({ startAngle: gap, endAngle: 2 * Math.PI - gap })!)
    .attr("fill", "#f0f0f0")

  const fgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(innerR)
    .outerRadius(outerR)
    .cornerRadius(4)

  const endAngle = targetAngle.value
  const startFrom = animate ? currentEndAngle.value : endAngle

  const path = g
    .append("path")
    .datum({ startAngle: gap, endAngle: Math.max(startFrom, gap) })
    .attr("d", (d) => fgArc(d)!)
    .attr("fill", props.color)

  if (animate && Math.abs(endAngle - startFrom) > 0.01) {
    path
      .transition()
      .duration(800)
      .ease(d3.easeCubicInOut)
      .attrTween("d", function (d) {
        const interpolate = d3.interpolate(d.endAngle, Math.max(endAngle, gap))
        return function (t) {
          d.endAngle = interpolate(t)
          return fgArc(d)!
        }
      })
  }

  currentEndAngle.value = endAngle
}

onMounted(() => {
  currentEndAngle.value = 0
  render(true)
  if (svgRef.value?.parentElement) {
    resizeObs = new ResizeObserver(() => render(false))
    resizeObs.observe(svgRef.value.parentElement)
  }
})
onUnmounted(() => resizeObs?.disconnect())
watch([targetAngle, () => props.color], () => render(true))
</script>

<template>
  <div class="arc-score" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg ref="svgRef" :width="size" :height="size" />
    <div class="arc-center">
      <span class="arc-value">{{ centerText }}</span>
      <span v-if="label" class="arc-label">{{ label }}</span>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.arc-score {
  @apply relative inline-flex items-center justify-center;
}

.arc-center {
  @apply absolute inset-0 flex flex-col items-center justify-center pointer-events-none;
}

.arc-value {
  @apply text-lg font-bold text-gray-800;
}

.arc-label {
  @apply text-xs text-gray-400 leading-tight text-center;
  max-width: 80%;
}
</style>
