import { ref } from "vue"
import { exportDashboardPdf } from "@/services/dashboardService"
import { useToast } from "@/composables/useToast"

function baseSelectorForMatch(selectorText: string): string {
  return selectorText
    .split(",")
    .map((part) => part.replace(/::[-a-zA-Z]+(\([^)]*\))?/g, "").trim())
    .filter(Boolean)
    .join(", ")
}

function selectorMatches(root: HTMLElement, selectorText: string): boolean {
  const selector = baseSelectorForMatch(selectorText)
  if (!selector) return false
  try {
    return (
      root.matches(selector) ||
      root.querySelector(selector) !== null ||
      document.documentElement.matches(selector) ||
      document.body.matches(selector)
    )
  } catch (e) {
    console.error(e)
    return false
  }
}

function mediaConditionMatches(mediaText: string): boolean {
  const normalized = mediaText.trim().toLowerCase()
  if (normalized === "print") return true
  if (normalized === "screen") return false
  try {
    return window.matchMedia(mediaText).matches
  } catch (e) {
    console.error(e)
    return false
  }
}

function supportsConditionMatches(conditionText: string): boolean {
  try {
    return CSS.supports(conditionText)
  } catch (e) {
    console.error(e)
    return false
  }
}

function collectMatchedRules(rules: CSSRuleList, root: HTMLElement, out: string[]) {
  for (const rule of Array.from(rules)) {
    const type = rule.constructor.name
    if (type === "CSSStyleRule") {
      const styleRule = rule as CSSStyleRule
      const isVendorOnly = /::-webkit-|::-moz-/.test(styleRule.selectorText)
      const cleanedSelector = baseSelectorForMatch(styleRule.selectorText)
      if (!isVendorOnly && cleanedSelector && selectorMatches(root, cleanedSelector)) {
        out.push(`${cleanedSelector} { ${styleRule.style.cssText} }`)
      }
    } else if (
      type === "CSSFontFaceRule" ||
      type === "CSSImportRule" ||
      type === "CSSKeyframesRule"
    ) {
      continue
    } else if (type === "CSSPropertyRule") {
      const propertyRule = rule as unknown as { name: string; initialValue: string | null }
      if (propertyRule.initialValue) {
        out.push(`:root { ${propertyRule.name}: ${propertyRule.initialValue}; }`)
      }
    } else if (type === "CSSMediaRule") {
      const mediaRule = rule as CSSMediaRule
      if (mediaConditionMatches(mediaRule.media.mediaText)) {
        collectMatchedRules(mediaRule.cssRules, root, out)
      }
    } else if (type === "CSSSupportsRule") {
      const supportsRule = rule as CSSSupportsRule
      if (supportsConditionMatches(supportsRule.conditionText)) {
        collectMatchedRules(supportsRule.cssRules, root, out)
      }
    } else if ("cssRules" in rule) {
      collectMatchedRules((rule as unknown as CSSGroupingRule).cssRules, root, out)
    }
  }
}

async function cssTextFromLinkedSheet(href: string): Promise<CSSRuleList | undefined> {
  try {
    const response = await fetch(href)
    const text = await response.text()
    const style = document.createElement("style")
    style.textContent = text
    document.head.appendChild(style)
    const rules = style.sheet?.cssRules
    style.remove()
    return rules
  } catch (error) {
    console.error(error)
    return undefined
  }
}

async function collectRelevantCss(root: HTMLElement): Promise<string> {
  const out: string[] = []

  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const rules = sheet.cssRules
      if (rules) collectMatchedRules(rules, root, out)
    } catch {
      if (sheet.href) {
        const rules = await cssTextFromLinkedSheet(sheet.href)
        if (rules) collectMatchedRules(rules, root, out)
      }
    }
  }

  return out.join("\n")
}

const PDF_PAGE_CSS = `
  @page {
    size: A4;
    margin: 1.5cm;
  }
  .widget-card {
    break-inside: avoid;
  }
`

function flexToGridForWeasyprint(css: string): string {
  return css.replace(/\{([^{}]*)\}/g, (whole, body: string) => {
    if (!/display\s*:\s*(?:inline-)?flex/.test(body)) return whole
    const isColumn = /flex-direction\s*:\s*column/.test(body)
    let newBody = body.replace(/display\s*:\s*(?:inline-)?flex/g, "display: grid")
    if (!isColumn) {
      newBody += " grid-auto-flow: column; grid-auto-columns: max-content;"
    }
    return `{${newBody}}`
  })
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const blobUrl = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = blobUrl
  a.download = filename
  a.click()
  URL.revokeObjectURL(blobUrl)
}

const SVG_STYLE_PROPS = [
  "fill",
  "fill-opacity",
  "stroke",
  "stroke-width",
  "stroke-opacity",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-dasharray",
  "opacity",
  "color",
  "font-family",
  "font-size",
  "font-weight",
  "font-style",
  "text-anchor",
  "dominant-baseline",
  "letter-spacing",
  "visibility"
]

// Convert SVG to PNG
function inlineSvgComputedStyles(live: SVGSVGElement, clone: SVGSVGElement) {
  const liveNodes = [live, ...Array.from(live.querySelectorAll("*"))]
  const cloneNodes = [clone, ...Array.from(clone.querySelectorAll("*"))]
  liveNodes.forEach((liveNode, i) => {
    const cloneNode = cloneNodes[i]
    if (!cloneNode) return
    const cs = window.getComputedStyle(liveNode)
    let inline = ""
    for (const prop of SVG_STYLE_PROPS) {
      const val = cs.getPropertyValue(prop)
      if (val) inline += `${prop}:${val};`
    }
    if (inline) cloneNode.setAttribute("style", inline)
  })
}

async function rasterizeSvgToPng(
  svg: SVGSVGElement,
  scale = 2
): Promise<{ src: string; width: number; height: number } | null> {
  const { width, height } = svg.getBoundingClientRect()
  const w = Math.round(width)
  const h = Math.round(height)
  if (w <= 0 || h <= 0) return null

  const clone = svg.cloneNode(true) as SVGSVGElement
  inlineSvgComputedStyles(svg, clone)
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg")
  clone.setAttribute("width", String(w))
  clone.setAttribute("height", String(h))
  if (!clone.hasAttribute("viewBox")) {
    clone.setAttribute("viewBox", `0 0 ${w} ${h}`)
  }

  const svgString = new XMLSerializer().serializeToString(clone)
  const svgUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgString)

  const img = new Image()
  await new Promise<void>((resolve, reject) => {
    img.onload = () => resolve()
    img.onerror = () => reject(new Error("SVG rasterization failed"))
    img.src = svgUrl
  })

  const canvas = document.createElement("canvas")
  canvas.width = w * scale
  canvas.height = h * scale
  const ctx = canvas.getContext("2d")
  if (!ctx) return null
  ctx.scale(scale, scale)
  ctx.drawImage(img, 0, 0, w, h)

  return { src: canvas.toDataURL("image/png"), width: w, height: h }
}

async function serializeWithRasterizedSvgs(element: HTMLElement): Promise<string> {
  const clone = element.cloneNode(true) as HTMLElement
  const liveSvgs = Array.from(element.querySelectorAll("svg"))
  const cloneSvgs = Array.from(clone.querySelectorAll("svg"))

  for (let i = 0; i < liveSvgs.length; i++) {
    const cloneSvg = cloneSvgs[i]
    if (!cloneSvg) continue
    let raster: Awaited<ReturnType<typeof rasterizeSvgToPng>> = null
    try {
      raster = await rasterizeSvgToPng(liveSvgs[i])
    } catch (e) {
      console.error(e)
    }
    if (!raster) continue
    const img = document.createElement("img")
    img.src = raster.src
    img.setAttribute("style", `width:${raster.width}px;height:${raster.height}px;`)
    cloneSvg.replaceWith(img)
  }

  return clone.outerHTML
}

export function usePdfExport() {
  const isExporting = ref(false)
  const toast = useToast()

  const exportElementToPdf = async (element: HTMLElement, filename = "rapport-iarbre.pdf") => {
    isExporting.value = true
    try {
      const css = flexToGridForWeasyprint(await collectRelevantCss(element))
      const body = await serializeWithRasterizedSvgs(element)
      const html = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>${css}\n${PDF_PAGE_CSS}</style>
  </head>
  <body>${body}</body>
</html>`

      const { data, error } = await exportDashboardPdf(html)
      if (error || !data) {
        throw error ?? new Error("Empty PDF response")
      }

      triggerBlobDownload(data, filename)
    } catch (error) {
      console.error(error)
      const isTimeout = error instanceof Error && error.message === "Request timed out"
      toast.add({
        severity: "error",
        summary: "Export impossible",
        detail: isTimeout
          ? "L'export a échoué : la génération du PDF a été arrêtée (délai dépassé). Merci de réessayer."
          : "Le rapport PDF n'a pas pu être généré. Merci de réessayer.",
        life: 5000,
        group: "br"
      })
    } finally {
      isExporting.value = false
    }
  }

  return { exportElementToPdf, isExporting }
}
