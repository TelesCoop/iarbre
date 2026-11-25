import { ref } from "vue"
import { useDashboardStore } from "@/stores/dashboard"
import { useToast } from "@/composables/useToast"
import { exportDashboardPdf } from "@/services/pdfExportService"

// Shared between every export button of the dashboard so that a second click
// anywhere on the page does not start a second generation.
const loading = ref(false)

export function useDashboardPdfExport() {
  const store = useDashboardStore()
  const toast = useToast()

  const pdfFilename = () => {
    const zone =
      store.selectedScale === "zone"
        ? "zone-personnalisee"
        : (store.selectedCity?.name ?? "metropole-de-lyon")
    const slug = zone
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
    return `iarbre-${slug}-${new Date().toISOString().slice(0, 10)}.pdf`
  }

  const exportToPdf = async () => {
    if (loading.value) return
    loading.value = true
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 6000)
    toast.add({
      severity: "info",
      summary: "Génération du rapport en cours...",
      group: "br",
      life: 0
    })
    try {
      const blob = await exportDashboardPdf(store.currentScope, controller.signal)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = pdfFilename()
      a.click()
      URL.revokeObjectURL(url)
      toast.removeAll()
      toast.add({ severity: "success", summary: "Rapport généré", group: "br" })
    } catch {
      toast.removeAll()
      toast.add({
        severity: "error",
        summary: "La génération du rapport a échoué",
        group: "br"
      })
    } finally {
      clearTimeout(timer)
      loading.value = false
    }
  }

  return { loading, exportToPdf }
}
