<script lang="ts" setup>
import { ref } from "vue"
import AppButton from "@/components/shared/AppButton.vue"
import { useDashboardStore } from "@/stores/dashboard"
import { useToast } from "@/composables/useToast"
import { exportDashboardPdf } from "@/services/pdfExportService"

const store = useDashboardStore()
const toast = useToast()
const loading = ref(false)

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
    a.download = "rapport.pdf"
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
</script>

<template>
  <footer
    class="flex flex-col items-center gap-4 p-6 rounded-xl bg-primary-50 border border-primary-100 mt-4 print:hidden"
  >
    <div class="text-center">
      <h2 class="text-lg font-bold text-gray-900">Exporter le rapport</h2>
      <p class="text-sm text-gray-600 mt-1">
        Téléchargez ce tableau de bord au format PDF pour le partager ou le consulter hors ligne.
      </p>
    </div>
    <AppButton variant="primary" size="lg" :disabled="loading" @click="exportToPdf">
      <template #icon-left>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          width="18"
          height="18"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
      </template>
      Télécharger le rapport complet
    </AppButton>
  </footer>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>
