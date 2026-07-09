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

function triggerBlobDownload(blob: Blob, filename: string) {
  const blobUrl = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = blobUrl
  a.download = filename
  a.click()
  URL.revokeObjectURL(blobUrl)
}

export function usePdfExport() {
  const isExporting = ref(false)
  const toast = useToast()

  const exportElementToPdf = async (element: HTMLElement, filename = "rapport-iarbre.pdf") => {
    isExporting.value = true
    try {
      const css = await collectRelevantCss(element)
      const html = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>${css}\n${PDF_PAGE_CSS}</style>
  </head>
  <body>${element.outerHTML}</body>
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
