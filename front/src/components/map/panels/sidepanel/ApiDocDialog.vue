<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { ref } from "vue"
import { getFullBaseApiUrl } from "@/api"
import AccordionSection from "./apiDoc/AccordionSection.vue"
import QgisConnectionCard from "./apiDoc/QgisConnectionCard.vue"
import ManualRequestSection from "./apiDoc/ManualRequestSection.vue"
import type { RequestParam } from "./apiDoc/types"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wfs" | "wms" | "raster" | null>(null)

const toggle = (service: "wfs" | "wms" | "raster") => {
  expanded.value = expanded.value === service ? null : service
}

const origin = window.location.origin
const wfsBase = `${origin}/api/wfs/`
const wmsBase = `${origin}/api/wms/`

const defaultTypename = "iarbre:plantability"

const wfsFullUrl = `${wfsBase}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=${defaultTypename}&OUTPUTFORMAT=geojson`

const wfsParams: RequestParam[] = [
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

const wmsFullUrl = `${wmsBase}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=${defaultTypename}&BBOX=45.5,4.7,46.0,5.2&CRS=EPSG:4326&WIDTH=800&HEIGHT=600&FORMAT=image/png`

const wmsParams: RequestParam[] = [
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
        <AccordionSection :open="expanded === 'wfs'" @toggle="toggle('wfs')">
          <template #header>
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
          </template>

          <div class="bg-amber-50 px-3 py-3 rounded-md">
            <p class="text-xs font-bold text-amber-700 mb-1">Téléchargement volumineux</p>
            <p class="text-xs text-amber-800">
              Le jeu complet contient 21 millions de tuiles. Utilisez un filtre BBOX ou CQL_FILTER
              (voir paramètres avancés) pour limiter le volume. Pour une consultation rapide,
              préférez le téléchargement raster ci-dessous.
            </p>
          </div>

          <QgisConnectionCard
            :base-url="wfsBase"
            :steps="[
              `Onglet &quot;Couche&quot; → &quot;Ajouter une couche&quot; → &quot;WFS&quot;`,
              `Collez l'URL ci-dessous, puis cliquez sur &quot;Connexion&quot;`
            ]"
          />

          <ManualRequestSection
            url-label="URL du service (exemple)"
            :url="wfsFullUrl"
            :params="wfsParams"
          />
        </AccordionSection>
      </div>

      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">FLUX WMS</p>
        <AccordionSection :open="expanded === 'wms'" @toggle="toggle('wms')">
          <template #header>
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
          </template>

          <QgisConnectionCard
            :base-url="wmsBase"
            :steps="[
              `Onglet &quot;Couche&quot; → &quot;Ajouter une couche&quot; → &quot;WMS/WMTS&quot;`,
              `Collez l'URL ci-dessous, puis cliquez sur &quot;Connexion&quot;`
            ]"
          />

          <ManualRequestSection
            url-label="URL GetMap (exemple)"
            :url="wmsFullUrl"
            :params="wmsParams"
          />
        </AccordionSection>
      </div>

      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">TÉLÉCHARGEMENT RASTER</p>
        <AccordionSection
          :open="expanded === 'raster'"
          body-class="px-3 py-3 space-y-2"
          @toggle="toggle('raster')"
        >
          <template #header>
            <span class="flex-none font-mono font-bold text-xs text-gray-600 w-8">TIF</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">REST - GeoTIFF</p>
              <p class="text-xs text-gray-500">
                Téléchargement direct pour récupérer les calques en entier au format GeoTIFF
                (EPSG:2154).
              </p>
            </div>
          </template>

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
        </AccordionSection>
      </div>
    </div>
  </AppDialog>
</template>
