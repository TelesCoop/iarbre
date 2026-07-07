<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { ref } from "vue"
import { getFullBaseApiUrl } from "@/api"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wfs" | "wms" | "raster" | null>(null)

const toggle = (service: "wfs" | "wms" | "raster") => {
  expanded.value = expanded.value === service ? null : service
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}

const origin = window.location.origin
const wfsBase = `${origin}/api/wfs/`
const wmsBase = `${origin}/api/wms/`

const defaultTypename = "iarbre:plantability"

// Accordion state for the "build a request manually" section (collapsed by
// default — most visitors only need the QGIS base URL, not the raw params)
const wfsRequestOpen = ref(false)

const wfsFullUrl = `${wfsBase}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=${defaultTypename}&OUTPUTFORMAT=geojson`

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
    value: defaultTypename,
    desc: "Jeu de données à récupérer — voir GetTypes pour la liste complète"
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
  },
  {
    key: "CQL_FILTER",
    value: "city_code='69123'",
    desc: "Filtre par commune (code INSEE) — réduit le volume de données"
  }
]

interface RasterDataset {
  label: string
  url: string
}

const rasterUrl = (key: string) => `${getFullBaseApiUrl()}/rasters/${key}/`

type DownloadStatus = "idle" | "loading" | "success" | "error"
const downloadStatus = ref<Record<string, DownloadStatus>>({})

const downloadRaster = async (url: string) => {
  downloadStatus.value[url] = "loading"
  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const disposition = response.headers.get("Content-Disposition")
    let filename = url.split("/").filter(Boolean).pop() || "raster.tif"
    const match = disposition?.match(/filename="?([^"]+)"?/)
    if (match) filename = match[1]
    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = blobUrl
    a.download = filename
    a.click()
    URL.revokeObjectURL(blobUrl)
    downloadStatus.value[url] = "success"
  } catch {
    downloadStatus.value[url] = "error"
    return
  }
  setTimeout(() => {
    if (downloadStatus.value[url] === "success") downloadStatus.value[url] = "idle"
  }, 2000)
}

const rasterDatasets: RasterDataset[] = [
  { label: "Plantabilité (couleurs)", url: rasterUrl("plantability_colors") },
  { label: "Plantabilité (données brutes)", url: rasterUrl("plantability") },
  { label: "Végéstrate", url: rasterUrl("vegestrate") },
  { label: "Végéstrate avec hauteurs", url: rasterUrl("vegestrate_ndsm") },
  { label: "Vulnérabilité chaleur (couleurs)", url: rasterUrl("vulnerability_colors") },
  { label: "Vulnérabilité chaleur (données brutes)", url: rasterUrl("vulnerability") },
  { label: "Zones climatiques locales (couleurs)", url: rasterUrl("lcz_colors") },
  { label: "Zones climatiques locales (données brutes)", url: rasterUrl("lcz") }
]

const wmsRequestOpen = ref(false)

const wmsFullUrl = `${wmsBase}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=${defaultTypename}&BBOX=45.5,4.7,46.0,5.2&CRS=EPSG:4326&WIDTH=800&HEIGHT=600&FORMAT=image/png`

const wmsParams: Param[] = [
  { key: "SERVICE", value: "WMS", desc: "Type de service", fixed: true },
  { key: "VERSION", value: "1.3.0", desc: "Version du protocole", fixed: true },
  {
    key: "REQUEST",
    value: "GetMap",
    desc: "Type de requete (GetMap ou GetCapabilities)",
    fixed: true
  },
  {
    key: "LAYERS",
    value: defaultTypename,
    desc: "Couche à afficher — voir GetLayers pour la liste complète"
  },
  {
    key: "BBOX",
    value: "45.5,4.7,46.0,5.2",
    desc: "Emprise (lat_min,lon_min,lat_max,lon_max en EPSG:4326 pour WMS 1.3.0)"
  },
  {
    key: "CRS",
    value: "EPSG:4326",
    desc: "Systeme de coordonnees - EPSG:4326, EPSG:3857, EPSG:2154"
  },
  { key: "WIDTH", value: "800", desc: "Largeur de l'image en pixels" },
  { key: "HEIGHT", value: "600", desc: "Hauteur de l'image en pixels" },
  { key: "FORMAT", value: "image/png", desc: "Format de sortie", fixed: true }
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
        <p class="text-2xs text-primary-100">ia·rbre - Métropole de Lyon</p>
      </div>
    </template>

    <div class="flex flex-col bg-white -m-6 p-6 gap-4">
      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">FLUX WFS</p>
        <div class="border border-gray-200 rounded-md overflow-hidden">
          <button
            :class="[
              'flex w-full items-center gap-2 px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
              expanded === 'wfs' ? 'rounded-t-md border-b-0' : 'rounded-md'
            ]"
            @click="toggle('wfs')"
          >
            <span class="flex-none font-mono font-bold text-xs text-primary-800 w-8">WFS</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">WEB FEATURE SERVICE</p>
              <p class="text-xs text-gray-500">
                Objets géographiques vecteur, interrogeables et filtrables par commune.
              </p>
            </div>
            <div class="flex gap-1 shrink-0">
              <span
                v-for="fmt in ['GeoJSON', 'GML', 'CSV']"
                :key="fmt"
                class="font-mono font-bold text-2xs text-white bg-primary-800 px-1.5 py-0.5 rounded"
                >{{ fmt }}</span
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
              :class="expanded === 'wfs' ? 'rotate-180' : ''"
            >
              <path d="M2 4L6 8L10 4" />
            </svg>
          </button>

          <Transition name="accordion">
            <div v-if="expanded === 'wfs'" class="border-t border-gray-100 px-3 py-3 space-y-4">
              <div class="bg-amber-50 px-3 py-3 rounded-md">
                <p class="text-xs font-bold text-amber-700 mb-1">Téléchargement volumineux</p>
                <p class="text-xs text-amber-800">
                  Le jeu complet contient 21 millions de tuiles. Utilisez un filtre BBOX ou
                  CQL_FILTER (voir paramètres avancés) pour limiter le volume. Pour une consultation
                  rapide, préférez le téléchargement raster ci-dessous.
                </p>
              </div>

              <div class="border border-primary-300 rounded-lg overflow-hidden shadow-sm">
                <div class="flex items-center gap-2 px-3 py-2 bg-primary-500">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M9 17H7A5 5 0 017 7h2M15 7h2a5 5 0 010 10h-2M8 12h8" />
                  </svg>
                  <span class="text-xs font-bold text-white tracking-wide">CONNEXION QGIS</span>
                </div>
                <div class="px-3 py-3 bg-primary-50 space-y-2.5">
                  <ol class="text-xs text-primary-900 space-y-1 list-decimal list-inside">
                    <li>Onglet "Couche" → "Ajouter une couche" → "WFS"</li>
                    <li>Collez l'URL ci-dessous, puis cliquez sur "Connexion"</li>
                  </ol>
                  <div
                    class="flex items-center gap-2 bg-white border border-primary-200 rounded-md pl-2.5 pr-1.5 py-1.5"
                  >
                    <span class="font-mono text-xs text-primary-700 flex-1 truncate">{{
                      wfsBase
                    }}</span>
                    <button
                      type="button"
                      class="text-2xs font-semibold text-white bg-primary-500 hover:bg-primary-600 transition-colors rounded px-2 py-1 shrink-0"
                      @click="copyToClipboard(wfsBase)"
                    >
                      Copier
                    </button>
                  </div>
                </div>
              </div>

              <div class="border border-gray-200 rounded-md overflow-hidden">
                <button
                  type="button"
                  :class="[
                    'flex w-full items-center justify-between px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
                    wfsRequestOpen ? 'border-b border-gray-200' : ''
                  ]"
                  @click="wfsRequestOpen = !wfsRequestOpen"
                >
                  <span class="text-2xs font-bold text-gray-500 tracking-wider"
                    >CONSTRUIRE LA REQUÊTE MANUELLEMENT</span
                  >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="text-gray-400 transition-transform duration-200"
                    :class="wfsRequestOpen ? 'rotate-180' : ''"
                  >
                    <path d="M2 4L6 8L10 4" />
                  </svg>
                </button>
                <Transition name="accordion">
                  <div v-if="wfsRequestOpen" class="p-2.5 space-y-3">
                    <div class="bg-gray-50 border border-gray-200 rounded-md overflow-hidden">
                      <div
                        class="flex items-center justify-between px-2.5 py-2 border-b border-gray-100"
                      >
                        <span class="text-xs text-gray-400">URL du service (exemple)</span>
                        <button
                          class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
                          @click="copyToClipboard(wfsFullUrl)"
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
                      <button
                        type="button"
                        class="raster-url block w-full text-left px-2.5 py-2 bg-white font-mono text-xs text-primary-500 hover:text-primary-700 cursor-pointer"
                        @click="copyToClipboard(wfsFullUrl)"
                      >
                        {{ wfsFullUrl }}
                      </button>
                    </div>

                    <div class="border border-gray-200 rounded-md overflow-hidden">
                      <div
                        class="grid grid-cols-[1fr_1fr_2fr] text-2xs font-bold text-gray-400 tracking-wider border-b border-gray-200 bg-gray-50 px-2.5 py-2"
                      >
                        <span>PARAMÈTRE</span>
                        <span>VALEUR</span>
                        <span>DESCRIPTION</span>
                      </div>
                      <div
                        v-for="(param, i) in wfsParams"
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
                </Transition>
              </div>
            </div>
          </Transition>
        </div>
      </div>

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
                Tuiles d'image raster, intégrables dans QGIS, ArcGIS ou autre SIG/cartographie.
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
              <div class="border border-primary-300 rounded-lg overflow-hidden shadow-sm">
                <div class="flex items-center gap-2 px-3 py-2 bg-primary-500">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M9 17H7A5 5 0 017 7h2M15 7h2a5 5 0 010 10h-2M8 12h8" />
                  </svg>
                  <span class="text-xs font-bold text-white tracking-wide">CONNEXION QGIS</span>
                </div>
                <div class="px-3 py-3 bg-primary-50 space-y-2.5">
                  <ol class="text-xs text-primary-900 space-y-1 list-decimal list-inside">
                    <li>Onglet "Couche" → "Ajouter une couche" → "WMS/WMTS"</li>
                    <li>Collez l'URL ci-dessous, puis cliquez sur "Connexion"</li>
                  </ol>
                  <div
                    class="flex items-center gap-2 bg-white border border-primary-200 rounded-md pl-2.5 pr-1.5 py-1.5"
                  >
                    <span class="font-mono text-xs text-primary-700 flex-1 truncate">{{
                      wmsBase
                    }}</span>
                    <button
                      type="button"
                      class="text-2xs font-semibold text-white bg-primary-500 hover:bg-primary-600 transition-colors rounded px-2 py-1 shrink-0"
                      @click="copyToClipboard(wmsBase)"
                    >
                      Copier
                    </button>
                  </div>
                </div>
              </div>

              <div class="border border-gray-200 rounded-md overflow-hidden">
                <button
                  type="button"
                  :class="[
                    'flex w-full items-center justify-between px-2.5 py-2 bg-gray-100 text-left transition-colors duration-200 hover:bg-gray-200',
                    wmsRequestOpen ? 'border-b border-gray-200' : ''
                  ]"
                  @click="wmsRequestOpen = !wmsRequestOpen"
                >
                  <span class="text-2xs font-bold text-gray-500 tracking-wider"
                    >CONSTRUIRE LA REQUÊTE MANUELLEMENT</span
                  >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="text-gray-400 transition-transform duration-200"
                    :class="wmsRequestOpen ? 'rotate-180' : ''"
                  >
                    <path d="M2 4L6 8L10 4" />
                  </svg>
                </button>
                <Transition name="accordion">
                  <div v-if="wmsRequestOpen" class="p-2.5 space-y-3">
                    <div class="bg-gray-50 border border-gray-200 rounded-md overflow-hidden">
                      <div
                        class="flex items-center justify-between px-2.5 py-2 border-b border-gray-100"
                      >
                        <span class="text-xs text-gray-400">URL GetMap (exemple)</span>
                        <button
                          class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
                          @click="copyToClipboard(wmsFullUrl)"
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
                      <button
                        type="button"
                        class="raster-url block w-full text-left px-2.5 py-2 bg-white font-mono text-xs text-primary-500 hover:text-primary-700 cursor-pointer"
                        @click="copyToClipboard(wmsFullUrl)"
                      >
                        {{ wmsFullUrl }}
                      </button>
                    </div>

                    <div class="border border-gray-200 rounded-md overflow-hidden">
                      <div
                        class="grid grid-cols-[1fr_1fr_2fr] text-2xs font-bold text-gray-400 tracking-wider border-b border-gray-200 bg-gray-50 px-2.5 py-2"
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
                </Transition>
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
                Téléchargement direct pour récupérer les calques en entier au format GeoTIFF
                (EPSG:2154).
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
                v-for="dataset in rasterDatasets"
                :key="dataset.url"
                class="py-2 px-2.5 bg-gray-50 border border-gray-200 rounded-md"
              >
                <div class="flex items-center justify-between gap-2 mb-1">
                  <span class="text-sm text-gray-700">{{ dataset.label }}</span>
                  <button
                    type="button"
                    :disabled="downloadStatus[dataset.url] === 'loading'"
                    :class="[
                      'text-xs font-medium text-white transition-colors rounded px-2 py-1 shrink-0',
                      downloadStatus[dataset.url] === 'loading'
                        ? 'bg-primary-300 cursor-wait'
                        : downloadStatus[dataset.url] === 'error'
                          ? 'bg-red-500 hover:bg-red-600 cursor-pointer'
                          : downloadStatus[dataset.url] === 'success'
                            ? 'bg-green-600 cursor-pointer'
                            : 'bg-primary-500 hover:bg-primary-600 cursor-pointer'
                    ]"
                    @click="downloadRaster(dataset.url)"
                  >
                    <span v-if="downloadStatus[dataset.url] === 'loading'">Téléchargement…</span>
                    <span v-else-if="downloadStatus[dataset.url] === 'success'">Téléchargé ✓</span>
                    <span v-else-if="downloadStatus[dataset.url] === 'error'">Échec</span>
                    <span v-else>Télécharger</span>
                  </button>
                </div>
                <p v-if="downloadStatus[dataset.url] === 'error'" class="text-2xs text-red-600">
                  Le téléchargement a échoué. Vérifiez votre connexion ou réessayez.
                </p>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </AppDialog>
</template>

<style scoped>
@reference "@/styles/main.css";

.raster-url {
  word-break: break-all;
  overflow-wrap: anywhere;
}

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
