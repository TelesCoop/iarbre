<script lang="ts" setup>
import AppDialog from "@/components/shared/AppDialog.vue"
import { computed, ref } from "vue"
import { getFullBaseApiUrl } from "@/api"
import { useMapStore } from "@/stores/map"
import { RASTER_LAYERS, buildRasterUrl, formatHour } from "@/utils/rasterLayers"
import AccordionSection from "./apiDoc/AccordionSection.vue"
import QgisConnectionCard from "./apiDoc/QgisConnectionCard.vue"
import ManualRequestSection from "./apiDoc/ManualRequestSection.vue"
import type { RequestParam } from "./apiDoc/types"

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: "update:visible", value: boolean): void }>()

const expanded = ref<"wms" | "raster" | null>(null)

const toggle = (service: "wms" | "raster") => {
  expanded.value = expanded.value === service ? null : service
}

const origin = window.location.origin
const wmsBase = `${origin}/api/wms/`

const defaultWmsLayer = "iarbre:PET_index_1m_2090_h16"

interface RasterDataset {
  label: string
  url: string
}

const mapStore = useMapStore()

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

const rasterDatasets = computed<RasterDataset[]>(() => {
  const baseApiUrl = getFullBaseApiUrl()
  return RASTER_LAYERS.flatMap((layer) =>
    layer.hourly
      ? [
          {
            label: `${layer.label} (${formatHour(mapStore.selectedHour)})`,
            url: buildRasterUrl(baseApiUrl, layer, mapStore.selectedHour)
          },
          { label: `${layer.label} (toutes les heures)`, url: buildRasterUrl(baseApiUrl, layer) }
        ]
      : [{ label: layer.label, url: buildRasterUrl(baseApiUrl, layer) }]
  )
})

const wmsFullUrl = `${wmsBase}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=${defaultWmsLayer}&BBOX=45.5,4.7,46.0,5.2&CRS=EPSG:4326&WIDTH=800&HEIGHT=600&FORMAT=image/png`

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
    value: defaultWmsLayer,
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
        <h3 class="text-sm font-bold text-primary-500">
          Obtenez de l'aide
          <a
            href="https://erasme.notion.site/R-cup-rer-les-donn-es-d-IArbre-39844e49a3ad807cb418ef62f04b0b5d?pvs=74"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary-500 underline hover:text-primary-700"
            >ici</a
          >.
        </h3>
      </div>
      <div>
        <p class="text-xs font-bold text-gray-400 tracking-wider mb-2">FLUX WMS</p>
        <AccordionSection :open="expanded === 'wms'" @toggle="toggle('wms')">
          <template #header>
            <span class="flex-none font-mono font-bold text-xs text-primary-800 w-8">WMS</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">WEB MAP SERVICE (QGIS)</p>
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
              <p class="text-sm font-semibold text-gray-800">Téléchargement direct des rasters</p>
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
