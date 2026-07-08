<script lang="ts" setup>
import AppButton from "@/components/shared/AppButton.vue"
import { usePdfExport } from "@/composables/usePdfExport"

const { exportElementToPdf, isExporting } = usePdfExport()

const exportToPdf = () => {
  const content = document.querySelector<HTMLElement>(".dashboard-content")
  if (!content) return
  exportElementToPdf(content, "rapport-iarbre.pdf")
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
    <AppButton variant="primary" size="lg" :loading="isExporting" @click="exportToPdf">
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
      {{ isExporting ? "Génération du PDF..." : "Télécharger le rapport complet" }}
    </AppButton>
  </footer>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>
