import { ref, onMounted, onUnmounted, watch, type Ref, type WatchSource } from "vue"
import * as d3 from "d3"

export interface D3ChartContext {
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>
  width: number
  height: number
}

export function useD3Chart(
  renderFn: (ctx: D3ChartContext, animate: boolean) => void,
  watchSources: WatchSource[]
): { svgRef: Ref<SVGSVGElement | null> } {
  const svgRef = ref<SVGSVGElement | null>(null)
  let resizeObserver: ResizeObserver | null = null

  function render(animate: boolean) {
    if (!svgRef.value) return
    const svg = d3.select(svgRef.value)
    svg.selectAll("*").remove()

    const rect = svgRef.value.getBoundingClientRect()
    const { width, height } = rect
    if (width <= 0 || height <= 0) return

    renderFn({ svg, width, height }, animate)
  }

  onMounted(() => {
    render(true)
    if (svgRef.value?.parentElement) {
      resizeObserver = new ResizeObserver(() => render(false))
      resizeObserver.observe(svgRef.value.parentElement)
    }
  })

  onUnmounted(() => resizeObserver?.disconnect())

  watch(watchSources, () => render(true))

  return { svgRef }
}
