<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { ref } from "vue"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wms" | "wfs" | null>(null)

const toggle = (service: "wms" | "wfs") => {
  expanded.value = expanded.value === service ? null : service
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}

const wfsBase = "https://carte.iarbre.fr/api/wfs/plantability/"

interface Param {
  key: string
  value: string
  desc: string
  fixed?: boolean
}

const wfsParams: Param[] = [
  { key: "SERVICE", value: "WFS", desc: "Type de service", fixed: true },
  { key: "VERSION", value: "2.0.0", desc: "Version du protocole", fixed: true },
  { key: "REQUEST", value: "GetFeature", desc: "Type de requête", fixed: true },
  { key: "TYPENAMES", value: "app:tile", desc: "Jeu de données à récupérer", fixed: true },
  { key: "OUTPUTFORMAT", value: "geojson", desc: "Format de sortie — geojson, csv, gml" },
  {
    key: "CRS",
    value: "EPSG:4326",
    desc: "Système de coordonnées — ex. EPSG:4326, EPSG:2154, EPSG:3857"
  },
  {
    key: "BBOX",
    value: "minLat,minLon,maxLat,maxLon",
    desc: "Emprise géographique en degrés décimaux"
  }
]
</script>

<template>
  <AppDialog
    :visible="visible"
    width="48rem"
    header-class="!bg-primary-900 !border-primary-700"
    close-class="!text-white/50 hover:!bg-white/10 hover:!text-white"
    @update:visible="emit('update:visible', $event)"
  >
    <template #header>
      <div class="flex-1">
        <h2 class="text-lg font-bold text-white">Export des données</h2>
        <p class="text-2xs text-green-500">ia·rbre · Métropole de Lyon</p>
      </div>
    </template>

    <div class="flex flex-col bg-off-white -m-6 p-6">
      <p class="text-sm font-bold text-primary-500 mb-1">API &amp; flux WFS</p>

      <div class="flex flex-col gap-2">
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <button
            class="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors"
            @click="toggle('wfs')"
          >
            <span class="text-gray-300 text-base shrink-0">›</span>
            <div
              class="w-11 h-11 shrink-0 rounded-md border border-[#cc7a5a] bg-[#fff8f5] flex items-center justify-center"
            >
              <span class="font-mono font-bold text-xs text-[#1565c0]">WFS</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-800">WEB FEATURE SERVICE</p>
              <p class="text-xs text-gray-500">
                Service de récupération d'objets géographiques vecteur, interrogeables et
                filtrables.
              </p>
            </div>
            <div class="flex gap-1.5 shrink-0">
              <span
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >GeoJSON</span
              >
              <span
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >GML</span
              >
              <span
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >CSV</span
              >
            </div>
          </button>

          <div v-if="expanded === 'wfs'" class="border-t border-gray-100 px-4 pt-3 pb-4 space-y-4">
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="flex items-center justify-between px-3 py-2 border-b border-gray-100">
                <span class="text-xs text-gray-400">URL du service</span>
                <button
                  class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
                  @click="
                    copyToClipboard(
                      `${wfsBase}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=app:tile&OUTPUTFORMAT=geojson`
                    )
                  "
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <rect x="9" y="9" width="13" height="13" rx="2" />
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                  </svg>
                  Copier
                </button>
              </div>
              <div class="px-3 py-2 bg-gray-50 font-mono text-xs leading-relaxed">
                <span class="text-gray-500">https://carte.iarbre.fr/api/wfs/</span
                ><span class="text-primary-500">plantability/</span><br />
                <span class="text-gray-300">?</span><span class="text-[#1565c0]">SERVICE</span
                ><span class="text-gray-300">=</span><span class="text-[#d97706]">WFS</span>
                <span class="text-gray-300"> &amp; </span><span class="text-[#1565c0]">VERSION</span
                ><span class="text-gray-300">=</span><span class="text-[#d97706]">2.0.0</span>
                <span class="text-gray-300"> &amp; </span><span class="text-[#1565c0]">REQUEST</span
                ><span class="text-gray-300">=</span><span class="text-[#d97706]">GetFeature</span
                ><br />
                <span class="text-gray-300">&amp; </span
                ><span class="text-[#1565c0]">TYPENAMES</span><span class="text-gray-300">=</span
                ><span class="text-[#d97706]">app:tile</span><br />
                <span class="text-gray-300">&amp; </span
                ><span class="text-[#1565c0]">OUTPUTFORMAT</span><span class="text-gray-300">=</span
                ><span class="text-[#d97706]">geojson</span>
              </div>
            </div>

            <div>
              <p class="text-2xs font-bold text-gray-400 tracking-wider mb-2">PARAMÈTRES</p>
              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div
                  class="grid grid-cols-[1fr_1fr_2fr] text-2xs font-bold text-gray-400 tracking-wider border-b border-gray-200 px-3 py-2"
                >
                  <span>PARAMÈTRE</span>
                  <span>VALEUR</span>
                  <span>DESCRIPTION</span>
                </div>
                <div
                  v-for="(param, i) in wfsParams"
                  :key="param.key"
                  class="grid grid-cols-[1fr_1fr_2fr] px-3 py-2 text-xs border-b border-gray-100 last:border-b-0"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
                >
                  <span class="font-mono text-[#1565c0]">{{ param.key }}</span>
                  <span class="font-mono text-[#d97706]">{{ param.value }}</span>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-600">{{ param.desc }}</span>
                    <span
                      v-if="param.fixed"
                      class="text-2xs text-gray-400 border border-gray-200 rounded px-1 shrink-0"
                      >fixe</span
                    >
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-blue-50 border-l-2 border-gray-400 px-3 py-3 rounded-r-lg">
              <p class="text-xs font-bold text--gray-400 mb-1">
                Intégration QGIS — Couche → Ajouter une couche → WFS.
              </p>
              <p class="text-xs">Collez l'URL de base : {{ wfsBase }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppDialog>
</template>
