import { ref } from "vue"
import { exportDashboardPdf } from "@/services/dashboardService"
import { useToast } from "@/composables/useToast"

async function cssTextFromLinkedSheet(href: string): Promise<string> {
  try {
    const response = await fetch(href)
    return await response.text()
  } catch (error) {
    console.error(error)
    return ""
  }
}

async function collectStylesheetsCss(): Promise<string> {
  const chunks: string[] = []

  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const rules = sheet.cssRules
      if (!rules) continue
      chunks.push(
        Array.from(rules)
          .map((rule) => rule.cssText)
          .join("\n")
      )
    } catch {
      // Cross-origin sheet without CORS headers: cssRules throws. Fall back
      // to fetching its text directly (works for same-origin/CORS-enabled hrefs).
      if (sheet.href) {
        chunks.push(await cssTextFromLinkedSheet(sheet.href))
      }
    }
  }

  return chunks.join("\n")
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
      const css = await collectStylesheetsCss()
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
      toast.add({
        severity: "error",
        summary: "Export impossible",
        detail: "Le rapport PDF n'a pas pu être généré. Merci de réessayer."
      })
    } finally {
      isExporting.value = false
    }
  }

  return { exportElementToPdf, isExporting }
}
