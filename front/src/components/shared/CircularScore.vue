<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue"
import * as d3 from "d3"
import type { ContextDataColorScheme, CircularScoreSize } from "@/types/contextData"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
import { getVulnerabilityColor } from "@/utils/vulnerability"

interface CircularScoreProps {
  score: number
  maxScore: number
  percentage: number
  label: string
  colorScheme: ContextDataColorScheme
  name?: string
  unit?: string
  size?: CircularScoreSize
}

const props = withDefaults(defineProps<CircularScoreProps>(), {
  name: undefined,
  unit: undefined,
  size: "normal"
})

const svgRef = ref<SVGSVGElement | null>(null)
const currentEndAngle = ref(0)

const SVG_SIZE = 120
const OUTER_R = SVG_SIZE / 2 - 2
const INNER_R = OUTER_R * 0.72
const GAP = 0.04

const arcColor = computed(() => {
  switch (props.colorScheme) {
    case "plantability": {
      const idx = PLANTABILITY_COLOR_MAP.indexOf(Math.round(props.score))
      if (idx !== -1 && idx + 1 < PLANTABILITY_COLOR_MAP.length) {
        return String(PLANTABILITY_COLOR_MAP[idx + 1])
      }
      return "#426A45"
    }
    case "vulnerability":
      return getVulnerabilityColor(props.score)
    case "climate":
      return "#426A45"
    default:
      return "#9CA3AF"
  }
})

const targetAngle = computed(() => {
  const ratio = Math.min(Math.max(props.percentage / 100, 0), 1)
  return ratio * 2 * Math.PI
})

const scoreDisplay = computed(() => {
  const scoreText = `${props.score}/${props.maxScore}`
  return props.unit ? `${scoreText} ${props.unit}` : scoreText
})

const ariaLabel = computed(() => {
  const baseName = props.name ? ` ${props.name}` : ""
  return `Score de ${props.label}${baseName}: ${props.score} sur ${props.maxScore}`
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case "small":
      return "w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24"
    case "large":
      return "w-24 h-24 sm:w-28 sm:h-28 md:w-32 md:h-32"
    case "normal":
    default:
      return "w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28"
  }
})

const labelSizeClass = computed(() => {
  switch (props.size) {
    case "small":
      return "text-xs"
    case "large":
      return "text-base"
    case "normal":
    default:
      return "text-sm"
  }
})

const scoreSizeClass = computed(() => {
  switch (props.size) {
    case "small":
      return "text-lg md:text-xl"
    case "large":
      return "text-2xl md:text-3xl"
    case "normal":
    default:
      return "text-xl md:text-2xl"
  }
})

function render(animate = true) {
  if (!svgRef.value) return
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const cx = SVG_SIZE / 2
  const cy = SVG_SIZE / 2
  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`)

  const bgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(INNER_R)
    .outerRadius(OUTER_R)

  g.append("path")
    .attr("d", bgArc({ startAngle: GAP, endAngle: 2 * Math.PI - GAP })!)
    .attr("fill", "#f0f0f0")

  const fgArc = d3
    .arc<{ startAngle: number; endAngle: number }>()
    .innerRadius(INNER_R)
    .outerRadius(OUTER_R)
    .cornerRadius(4)

  const endAngle = targetAngle.value
  const startFrom = animate ? currentEndAngle.value : endAngle

  const path = g
    .append("path")
    .datum({ startAngle: GAP, endAngle: Math.max(startFrom, GAP) })
    .attr("d", (d) => fgArc(d)!)
    .attr("fill", arcColor.value)

  if (animate && Math.abs(endAngle - startFrom) > 0.01) {
    path
      .transition()
      .duration(800)
      .ease(d3.easeCubicInOut)
      .attrTween("d", function (d) {
        const interpolate = d3.interpolate(d.endAngle, Math.max(endAngle, GAP))
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
})

onUnmounted(() => {})
watch([targetAngle, arcColor], () => render(true))
</script>

<template>
  <section :aria-labelledby="`score-section-${label}`" class="text-center">
    <h3 :id="`score-section-${label}`" class="sr-only">Score de {{ label }} {{ name }}</h3>

    <div class="relative inline-flex items-center justify-center" :class="sizeClasses">
      <svg
        ref="svgRef"
        :viewBox="`0 0 ${SVG_SIZE} ${SVG_SIZE}`"
        :aria-label="ariaLabel"
        class="w-full h-full"
        role="img"
        preserveAspectRatio="xMidYMid meet"
        data-cy="circular-progress"
      />

      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span v-if="name" :class="[labelSizeClass, 'text-gray-600', 'font-serif']"
          >{{ name }}:</span
        >
        <span v-else :class="[labelSizeClass, 'text-gray-600']">Score :</span>
        <span
          :class="[scoreSizeClass, 'font-bold']"
          :style="{ color: arcColor }"
          data-cy="context-data-score"
        >
          {{ scoreDisplay }}
        </span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
