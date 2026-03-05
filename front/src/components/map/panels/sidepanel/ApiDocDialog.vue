<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { ref } from "vue"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wfs" | "raster" | null>(null)

const toggle = (service: "wfs" | "raster") => {
  expanded.value = expanded.value === service ? null : service
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}

const wfsBase = "https://carte.iarbre.fr/api/wfs/"

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
  {
    key: "TYPENAMES",
    value: "iarbre:plantability",
    desc: "Jeu de données — iarbre:plantability ou iarbre:vegestrate"
  },
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
    header-class="!bg-primary-500 !border-primary-700"
    close-class="!text-white/50 hover:!bg-white/10 hover:!text-white"
    @update:visible="emit('update:visible', $event)"
  >
    <template #header>
      <div class="flex-1">
        <h2 class="text-lg font-bold text-white">Export des données</h2>
        <p class="text-2xs text-primary-100">ia·rbre · Métropole de Lyon</p>
      </div>
    </template>

    <div class="flex flex-col bg-off-white -m-6 p-6">
      <p class="text-sm font-bold text-primary-500 mb-1">Flux WFS</p>

      <div class="flex flex-col gap-2">
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <button
            class="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-200"
            @click="toggle('wfs')"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-gray-400 shrink-0 transition-transform duration-200"
              :class="expanded === 'wfs' ? 'rotate-90' : ''"
            >
              <polyline points="4 2 10 7 4 12" />
            </svg>
            <div
              class="w-11 h-11 shrink-0 rounded-md border border-scale-2 bg-primary-50 flex items-center justify-center"
            >
              <span class="font-mono font-bold text-xs text-primary-800">WFS</span>
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
                v-for="fmt in ['GeoJSON', 'GML', 'CSV']"
                :key="fmt"
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >{{ fmt }}</span
              >
            </div>
          </button>

          <Transition name="accordion">
            <div
              v-if="expanded === 'wfs'"
              class="border-t border-gray-100 px-4 pt-3 pb-4 space-y-4"
            >
              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="flex items-center justify-between px-3 py-2 border-b border-gray-100">
                  <span class="text-xs text-gray-400">URL du service</span>
                  <button
                    class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
                    @click="
                      copyToClipboard(
                        `${wfsBase}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=iarbre:plantability&OUTPUTFORMAT=geojson`
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
                  <span class="text-primary-500">https://carte.iarbre.fr/api/wfs/</span><br />
                  <span class="text-gray-300">?</span><span class="text-primary-800">SERVICE</span
                  ><span class="text-gray-300">=</span><span class="text-scale-3">WFS</span>
                  <span class="text-gray-300"> &amp; </span
                  ><span class="text-primary-800">VERSION</span><span class="text-gray-300">=</span
                  ><span class="text-scale-3">2.0.0</span> <span class="text-gray-300"> &amp; </span
                  ><span class="text-primary-800">REQUEST</span><span class="text-gray-300">=</span
                  ><span class="text-scale-3">GetFeature</span><br />
                  <span class="text-gray-300">&amp; </span
                  ><span class="text-primary-800">TYPENAMES</span
                  ><span class="text-gray-300">=</span
                  ><span class="text-scale-3">iarbre:plantability</span><br />
                  <span class="text-gray-300">&amp; </span
                  ><span class="text-primary-800">OUTPUTFORMAT</span
                  ><span class="text-gray-300">=</span><span class="text-scale-3">geojson</span>
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
                    <span class="font-mono text-primary-800">{{ param.key }}</span>
                    <span class="font-mono text-scale-3">{{ param.value }}</span>
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

              <div class="bg-primary-50 border-l-2 border-primary-500 px-3 py-3 rounded-r-lg">
                <p class="text-xs font-bold text-primary-700 mb-1">
                  Intégration QGIS — Couche → Ajouter une couche → WFS.
                </p>
                <p class="text-xs text-primary-800">Collez l'URL de base : {{ wfsBase }}</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <p class="text-sm font-bold text-primary-500 mt-4 mb-1">Téléchargement raster</p>

      <div class="flex flex-col gap-2">
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <button
            class="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-200"
            @click="toggle('raster')"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-gray-400 shrink-0 transition-transform duration-200"
              :class="expanded === 'raster' ? 'rotate-90' : ''"
            >
              <polyline points="4 2 10 7 4 12" />
            </svg>
            <div
              class="w-11 h-11 shrink-0 rounded-md border border-gray-300 bg-gray-50 flex items-center justify-center"
            >
              <span class="font-mono font-bold text-xs text-gray-600">TIF</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-800">REST — GeoTIFF</p>
              <p class="text-xs text-gray-500">
                Téléchargement du raster complet au format GeoTIFF (EPSG:2154).
              </p>
            </div>
          </button>
          <Transition name="accordion">
            <div v-if="expanded === 'raster'" class="border-t border-gray-100 px-4 pb-3 space-y-2">
              <div
                v-for="dataset in [
                  {
                    label: 'Plantabilité',
                    url: 'https://carte.iarbre.fr/api/rasters/plantability'
                  },
                  { label: 'Végéstrate', url: 'https://carte.iarbre.fr/api/rasters/vegestrate' }
                ]"
                :key="dataset.url"
                class="border border-gray-200 rounded-lg overflow-hidden"
              >
                <div class="flex items-center justify-between px-3 py-2">
                  <span class="text-xs text-gray-500">{{ dataset.label }}</span>
                  <div class="flex items-center gap-2">
                    <span class="font-mono text-xs text-primary-500 truncate">{{
                      dataset.url
                    }}</span>
                    <button
                      class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors shrink-0"
                      @click="copyToClipboard(dataset.url)"
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
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </AppDialog>
</template>

<style scoped>
.accordion-enter-active,
.accordion-leave-active {
  transition:
    max-height 0.2s ease,
    opacity 0.2s ease;
  max-height: 800px;
  overflow: hidden;
}

.accordion-enter-from,
.accordion-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
