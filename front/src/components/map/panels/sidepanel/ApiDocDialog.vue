<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { ref } from "vue"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wms" | "raster" | null>(null)

const toggle = (service: "wms" | "raster") => {
  expanded.value = expanded.value === service ? null : service
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}

const origin = window.location.origin
const wmsBase = `${origin}/api/wms/`

interface Param {
  key: string
  value: string
  desc: string
  fixed?: boolean
}

const wmsParams: Param[] = [
  { key: "SERVICE", value: "WMS", desc: "Type de service", fixed: true },
  { key: "VERSION", value: "1.3.0", desc: "Version du protocole", fixed: true },
  { key: "REQUEST", value: "GetMap", desc: "Type de requête", fixed: true },
  {
    key: "LAYERS",
    value: "iarbre:vegestrate_2023_ppv3",
    desc: "Couche à afficher — voir liste des couches disponibles"
  },
  {
    key: "CRS",
    value: "EPSG:4326",
    desc: "Système de coordonnées — EPSG:4326, EPSG:2154, EPSG:3857"
  },
  {
    key: "BBOX",
    value: "minLat,minLon,maxLat,maxLon",
    desc: "Emprise géographique (WMS 1.3.0 + EPSG:4326 : lat/lon)"
  },
  { key: "WIDTH", value: "800", desc: "Largeur de l'image en pixels" },
  { key: "HEIGHT", value: "600", desc: "Hauteur de l'image en pixels" },
  { key: "FORMAT", value: "image/png", desc: "Format de sortie", fixed: true }
]

const datasets = [
  {
    label: "Végéstrate 2018 - brut",
    url: `${origin}/api/rasters/vegestrate/?year=2018&resolution=02&postprocess=false`
  },
  {
    label: "Végéstrate 2018 - post-traité v3",
    url: `${origin}/api/rasters/vegestrate/?year=2018&resolution=02&postprocess=true&version=3`
  },
  {
    label: "Végéstrate 2023 - brut",
    url: `${origin}/api/rasters/vegestrate/?year=2023&resolution=02&postprocess=false`
  },
  {
    label: "Végéstrate 2023 - post-traité v1",
    url: `${origin}/api/rasters/vegestrate/?year=2023&resolution=02&postprocess=true&version=1`
  },
  {
    label: "Végéstrate 2023 - post-traité v2",
    url: `${origin}/api/rasters/vegestrate/?year=2023&resolution=02&postprocess=true&version=2`
  },
  {
    label: "Végéstrate 2023 - post-traité v3",
    url: `${origin}/api/rasters/vegestrate/?year=2023&resolution=02&postprocess=true&version=3`
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
        <p class="text-2xs text-primary-100">IA·rbre · Métropole de Lyon</p>
      </div>
    </template>

    <div class="flex flex-col bg-white -m-6 p-6 gap-4">
      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">FLUX WMS</p>
        <div class="border border-gray-200 rounded-md overflow-hidden">
          <button
            :class="[
              'flex w-full items-center gap-2 px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
              expanded === 'wms' ? 'rounded-t-md border-b-0' : 'rounded-md'
            ]"
            @click="toggle('wms')"
          >
            <span class="flex-none font-mono font-bold text-xs text-primary-800 w-8">WMS</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">WEB MAP SERVICE</p>
              <p class="text-xs text-gray-500">
                Flux raster tuilé à la volée, intégrable dans QGIS et autres clients SIG.
              </p>
            </div>
            <div class="flex gap-1 shrink-0">
              <span
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >PNG</span
              >
            </div>
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-gray-400 shrink-0 transition-transform duration-200"
              :class="expanded === 'wms' ? 'rotate-180' : ''"
            >
              <path d="M2 4L6 8L10 4" />
            </svg>
          </button>

          <Transition name="accordion">
            <div v-if="expanded === 'wms'" class="border-t border-gray-100 px-3 py-3 space-y-4">
              <div class="bg-gray-50 border border-gray-200 rounded-md overflow-hidden">
                <div class="flex items-center justify-between px-2.5 py-2 border-b border-gray-100">
                  <span class="text-xs text-gray-400">URL du service</span>
                  <button
                    class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
                    @click="
                      copyToClipboard(
                        `${wmsBase}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities`
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
                <div class="px-2.5 py-2 bg-white font-mono text-xs leading-relaxed">
                  <span class="text-primary-500">{{ wmsBase }}</span
                  ><br />
                  <span class="text-gray-300">?</span><span class="text-primary-800">SERVICE</span
                  ><span class="text-gray-300">=</span><span class="text-scale-3">WMS</span>
                  <span class="text-gray-300"> &amp; </span
                  ><span class="text-primary-800">VERSION</span><span class="text-gray-300">=</span
                  ><span class="text-scale-3">1.3.0</span> <span class="text-gray-300"> &amp; </span
                  ><span class="text-primary-800">REQUEST</span><span class="text-gray-300">=</span
                  ><span class="text-scale-3">GetCapabilities</span>
                </div>
              </div>

              <div>
                <p class="text-2xs font-bold text-gray-400 tracking-wider mb-2">
                  PARAMÈTRES GETMAP
                </p>
                <div class="border border-gray-200 rounded-md overflow-hidden">
                  <div
                    class="grid grid-cols-[1fr_1fr_2fr] text-2xs font-bold text-gray-400 tracking-wider border-b border-gray-200 bg-gray-100 px-2.5 py-2"
                  >
                    <span>PARAMÈTRE</span>
                    <span>VALEUR</span>
                    <span>DESCRIPTION</span>
                  </div>
                  <div
                    v-for="(param, i) in wmsParams"
                    :key="param.key"
                    class="grid grid-cols-[1fr_1fr_2fr] px-2.5 py-1.5 text-xs border-b border-gray-100 last:border-b-0"
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

              <div class="bg-primary-50 border-l-2 border-primary-500 px-3 py-3 rounded-r-md">
                <p class="text-xs font-bold text-primary-700 mb-1">
                  Intégration QGIS — Couche → Ajouter une couche → WMS/WMTS.
                </p>
                <p class="text-xs text-primary-800">Collez l'URL de base : {{ wmsBase }}</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">TÉLÉCHARGEMENT RASTER</p>
        <div class="border border-gray-200 rounded-md overflow-hidden">
          <button
            :class="[
              'flex w-full items-center gap-2 px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
              expanded === 'raster' ? 'rounded-t-md border-b-0' : 'rounded-md'
            ]"
            @click="toggle('raster')"
          >
            <span class="flex-none font-mono font-bold text-xs text-gray-600 w-8">TIF</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">REST - GeoTIFF</p>
              <p class="text-xs text-gray-500">
                Téléchargement du raster complet au format GeoTIFF (EPSG:2154).
              </p>
            </div>
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-gray-400 shrink-0 transition-transform duration-200"
              :class="expanded === 'raster' ? 'rotate-180' : ''"
            >
              <path d="M2 4L6 8L10 4" />
            </svg>
          </button>

          <Transition name="accordion">
            <div v-if="expanded === 'raster'" class="border-t border-gray-100 px-3 py-3 space-y-2">
              <div
                v-for="(dataset, i) in datasets"
                :key="dataset.url"
                class="flex items-center justify-between py-2 px-2.5 border border-gray-200 rounded-md"
                :class="i % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
              >
                <span class="text-sm text-gray-700 shrink-0">{{ dataset.label }}</span>
                <div class="flex items-center gap-2 min-w-0 ml-4">
                  <span class="font-mono text-xs text-primary-500 truncate">{{ dataset.url }}</span>
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
