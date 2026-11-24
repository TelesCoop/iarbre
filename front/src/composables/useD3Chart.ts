import { ref, onMounted, onUnmounted, watch, type Ref, type WatchSource } from "vue"
import * as d3 from "d3"
import "d3-transition"
import { shouldAnimate, supportsIntersectionObserver } from "@/utils/motion"

export interface D3ChartContext {
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>
  width: number
  height: number
}

/**
 * Renders a D3 chart in an SVG and keeps it in sync with its data and size.
 *
 * The first render is animated and only happens when the chart scrolls into
 * view. In print mode, or when the user prefers reduced motion, the chart is
 * drawn immediately in its final state.
 */
export function useD3Chart(
  renderFn: (ctx: D3ChartContext, animate: boolean) => void,
  watchSources: WatchSource[]
): { svgRef: Ref<SVGSVGElement | null> } {
  const svgRef = ref<SVGSVGElement | null>(null)
  let resizeObserver: ResizeObserver | null = null
  let intersectionObserver: IntersectionObserver | null = null
  let rendered = false
  let lastWidth = 0
  let lastHeight = 0

  function render(animate: boolean) {
    if (!svgRef.value) return
    const svg = d3.select(svgRef.value)
    svg.selectAll("*").remove()

    const rect = svgRef.value.getBoundingClientRect()
    const { width, height } = rect
    if (width <= 0 || height <= 0) return
    lastWidth = width
    lastHeight = height

    renderFn({ svg, width, height }, animate && shouldAnimate())
  }

  function firstRender(animate: boolean) {
    rendered = true
    render(animate)
    const parent = svgRef.value?.parentElement
    if (!parent) return
    resizeObserver = new ResizeObserver(() => {
      // The observer also fires right after `observe()`: only redraw (without
      // animation) when the size actually changed, so the first animated
      // render is not replaced by a static one.
      const rect = svgRef.value?.getBoundingClientRect()
      if (!rect || (rect.width === lastWidth && rect.height === lastHeight)) return
      render(false)
    })
    resizeObserver.observe(parent)
  }

  onMounted(() => {
    const el = svgRef.value
    if (!el) return
    if (!shouldAnimate() || !supportsIntersectionObserver()) {
      firstRender(false)
      return
    }
    intersectionObserver = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return
        intersectionObserver?.disconnect()
        intersectionObserver = null
        firstRender(true)
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.2 }
    )
    intersectionObserver.observe(el)
  })

  onUnmounted(() => {
    resizeObserver?.disconnect()
    intersectionObserver?.disconnect()
  })

  // Before the first render, new data is simply picked up by that render.
  watch(watchSources, () => {
    if (rendered) render(true)
  })

  return { svgRef }
}
