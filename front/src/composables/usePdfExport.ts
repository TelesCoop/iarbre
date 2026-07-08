import { ref } from "vue"
import { exportDashboardPdf } from "@/services/dashboardService"
import { useToast } from "@/composables/useToast"

// The app's compiled stylesheet contains every Tailwind utility used anywhere
// in the SPA (thousands of rules, incl. modern syntax like range media
// queries and `::-webkit-*` pseudo-elements WeasyPrint's CSS parser doesn't
// understand). Shipping it whole makes WeasyPrint's rule-matching crawl and
// spams warnings. Instead we keep only rules that actually apply to the
// captured subtree, resolving media/supports conditions in the browser first
// so WeasyPrint only ever sees plain, already-relevant declarations.

// Pseudo-elements (`::before`, `::-webkit-scrollbar`, ...) aren't valid
// arguments to matches()/querySelector() — strip them, we only need to know
// whether the *element* the rule would attach to exists in our subtree.
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
    return root.matches(selector) || root.querySelector(selector) !== null
  } catch {
    return false
  }
}

// WeasyPrint always renders in a print context regardless of what the
// browser reports, so force `print`/`screen` rather than asking matchMedia.
function mediaConditionMatches(mediaText: string): boolean {
  const normalized = mediaText.trim().toLowerCase()
  if (normalized === "print") return true
  if (normalized === "screen") return false
  try {
    return window.matchMedia(mediaText).matches
  } catch {
    return false
  }
}

function supportsConditionMatches(conditionText: string): boolean {
  try {
    return CSS.supports(conditionText)
  } catch {
    return false
  }
}

function collectMatchedRules(rules: CSSRuleList, root: HTMLElement, out: string[]) {
  for (const rule of Array.from(rules)) {
    const type = rule.constructor.name
    if (type === "CSSStyleRule") {
      const styleRule = rule as CSSStyleRule
      if (selectorMatches(root, styleRule.selectorText)) {
        out.push(styleRule.cssText)
      }
    } else if (type === "CSSFontFaceRule" || type === "CSSImportRule") {
      // No custom fonts are embedded and the export endpoint blocks network
      // fetches (SSRF guard), so these would only add noise/latency.
      continue
    } else if (type === "CSSKeyframesRule") {
      out.push(rule.cssText)
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
      // Cascade layers, @container, and other grouping at-rules: always
      // recurse, worst case we keep a handful of extra harmless rules.
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
      // Cross-origin sheet without CORS headers: cssRules throws. Fall back
      // to fetching its text directly (works for same-origin/CORS-enabled hrefs).
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
  .widget-card, section, .widgets-grid > * {
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
          ? "La génération du PDF a pris trop de temps. Merci de réessayer."
          : "Le rapport PDF n'a pas pu être généré. Merci de réessayer."
      })
    } finally {
      isExporting.value = false
    }
  }

  return { exportElementToPdf, isExporting }
}
