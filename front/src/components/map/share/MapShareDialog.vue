<script lang="ts" setup>
import { computed, onBeforeUnmount, ref, shallowRef, watch } from "vue"
import AppDialog from "@/components/shared/AppDialog.vue"
import AppButton from "@/components/shared/AppButton.vue"
import AppSelect from "@/components/shared/AppSelect.vue"
import IconCheck from "@/components/icons/IconCheck.vue"
import IconCopy from "@/components/icons/IconCopy.vue"
import IconImage from "@/components/icons/IconImage.vue"
import { fetchShortLink, useCopyLink } from "@/composables/useShortLink"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel, DataTypeToSourceDate, MapStyleToLabel } from "@/utils/enum"
import {
  DEFAULT_EXPORT_SIZE,
  EXPORT_FORMATS,
  ExportFormat,
  MAX_EXPORT_SIDE_PX,
  MIN_EXPORT_SIDE_PX,
  buildExportFileName,
  clampExportSide,
  encodeMapExport,
  generateMapExport
} from "@/utils/mapExport"
import type { ExportSize } from "@/utils/mapExport"

const props = defineProps<{
  modelValue: boolean
  mapId: string
}>()

const emit = defineEmits<{
  "update:modelValue": [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value)
})

interface ViewDetail {
  label: string
  value: string
}

const mapStore = useMapStore()
const { isCopied, copyLink } = useCopyLink()

const shortUrl = ref("")
const previewUrl = ref("")
const exportCanvas = shallowRef<HTMLCanvasElement | null>(null)
const exportBaseName = ref("")
const exportSize = ref<ExportSize>({ ...DEFAULT_EXPORT_SIZE })
const draftSize = ref<ExportSize>({ ...DEFAULT_EXPORT_SIZE })
const exportFormat = ref(ExportFormat.PNG)
const isGenerating = ref(false)
const isDownloading = ref(false)
const hasExportError = ref(false)
const details = ref<ViewDetail[]>([])
let generationId = 0
let shareId = 0

const sizeFields: { side: keyof ExportSize; label: string }[] = [
  { side: "width", label: "Largeur" },
  { side: "height", label: "Hauteur" }
]

const formatLabel = computed(
  () => EXPORT_FORMATS.find(({ value }) => value === exportFormat.value)?.label ?? ""
)

const releasePreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ""
  exportCanvas.value = null
}

const snapshotDetails = (lat: number, lng: number, zoom: number): ViewDetail[] => {
  const sourceDate = DataTypeToSourceDate[mapStore.selectedDataType]
  return [
    { label: "Couche", value: DataTypeToLabel[mapStore.selectedDataType] },
    { label: "Fond de carte", value: MapStyleToLabel[mapStore.selectedMapStyle] },
    {
      label: "Centre",
      value: `${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E · z${Math.round(zoom)}`
    },
    ...(sourceDate ? [{ label: "Millésime", value: sourceDate }] : [])
  ]
}

const renderExport = async () => {
  const currentId = ++generationId
  hasExportError.value = false
  isGenerating.value = true
  releasePreview()

  try {
    const canvas = await generateMapExport(
      mapStore.getMapInstance(props.mapId),
      DataTypeToLabel[mapStore.selectedDataType],
      document.querySelector<HTMLElement>(".legend-panel"),
      exportSize.value
    )
    const preview = await encodeMapExport(canvas, ExportFormat.JPEG)
    if (currentId !== generationId) return
    exportCanvas.value = canvas
    previewUrl.value = URL.createObjectURL(preview)
  } catch (error) {
    console.error(error)
    if (currentId === generationId) hasExportError.value = true
  } finally {
    if (currentId === generationId) isGenerating.value = false
  }
}

const prepareShare = () => {
  const map = mapStore.getMapInstance(props.mapId)
  const { lat, lng } = map.getCenter()
  const zoom = map.getZoom()
  details.value = snapshotDetails(lat, lng, zoom)
  exportBaseName.value = buildExportFileName(mapStore.selectedDataType, lat, lng, zoom)
  shortUrl.value = ""
  const currentShareId = ++shareId
  fetchShortLink().then((url) => {
    if (currentShareId === shareId) shortUrl.value = url
  })
  renderExport()
}

const downloadExport = async () => {
  if (!exportCanvas.value) return
  isDownloading.value = true
  try {
    const blob = await encodeMapExport(exportCanvas.value, exportFormat.value)
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `${exportBaseName.value}.${exportFormat.value}`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error(error)
    hasExportError.value = true
  } finally {
    isDownloading.value = false
  }
}

const handleCopy = () => {
  if (shortUrl.value) copyLink(shortUrl.value)
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      prepareShare()
    } else {
      generationId++
      shareId++
      releasePreview()
    }
  },
  { immediate: true }
)

const isSizeDirty = computed(
  () =>
    draftSize.value.width !== exportSize.value.width ||
    draftSize.value.height !== exportSize.value.height
)

const applySize = () => {
  if (isGenerating.value) return
  const size = {
    width: clampExportSide(draftSize.value.width, exportSize.value.width),
    height: clampExportSide(draftSize.value.height, exportSize.value.height)
  }
  draftSize.value = { ...size }
  if (size.width !== exportSize.value.width || size.height !== exportSize.value.height) {
    exportSize.value = size
  }
}

watch(exportSize, () => {
  if (props.modelValue) renderExport()
})

onBeforeUnmount(releasePreview)
</script>

<template>
  <AppDialog v-model:visible="visible" width="58rem" data-cy="share-view-dialog" modal>
    <template #header>
      <div class="flex flex-col gap-1">
        <span class="text-sm font-medium tracking-widest text-gray-500 uppercase">Partager</span>
        <h2 class="font-serif text-2xl lg:text-3xl text-primary-900 m-0">Exporter la vue</h2>
      </div>
    </template>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-10 font-sans">
      <div class="flex flex-col gap-4">
        <div
          class="relative w-full overflow-hidden rounded-xl bg-gray-100 shadow-md"
          :style="{ aspectRatio: `${exportSize.width} / ${exportSize.height}` }"
          data-cy="share-view-preview"
        >
          <img
            v-if="previewUrl"
            :src="previewUrl"
            alt="Aperçu de l'image exportée"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            class="absolute inset-0 flex items-center justify-center text-sm text-gray-500"
          >
            {{ hasExportError ? "L'aperçu n'a pas pu être généré." : "Génération de l'aperçu…" }}
          </div>
        </div>

        <form class="grid grid-cols-[1fr_1fr_auto] items-end gap-3" @submit.prevent="applySize">
          <label v-for="field in sizeFields" :key="field.side" class="flex flex-col gap-1.5">
            <span class="text-sm font-medium tracking-widest text-gray-500 uppercase">{{
              field.label
            }}</span>
            <span class="relative">
              <input
                v-model.number="draftSize[field.side]"
                type="number"
                :min="MIN_EXPORT_SIDE_PX"
                :max="MAX_EXPORT_SIDE_PX"
                step="1"
                :data-cy="`share-view-${field.side}-input`"
                class="w-full py-1.5 pl-3 pr-8 lg:py-2 lg:pl-4 bg-white border border-gray-200 rounded-lg text-xs lg:text-sm font-sans text-gray-700 outline-none transition-all hover:border-primary-500 focus:border-primary-500"
              />
              <span
                class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 pointer-events-none"
                >px</span
              >
            </span>
          </label>
          <AppButton
            type="submit"
            variant="outline"
            :disabled="!isSizeDirty || isGenerating"
            data-cy="share-view-apply-size-button"
          >
            Appliquer
          </AppButton>
        </form>

        <div class="flex flex-col gap-1.5">
          <span class="text-sm font-medium tracking-widest text-gray-500 uppercase">Format</span>
          <AppSelect
            v-model="exportFormat"
            :options="EXPORT_FORMATS"
            data-cy="share-view-format-select"
          />
        </div>

        <AppButton
          variant="gold"
          size="lg"
          full-width
          :disabled="!exportCanvas"
          :loading="isGenerating || isDownloading"
          data-cy="share-view-export-button"
          @click="downloadExport"
        >
          <template #icon-left>
            <IconImage :size="20" />
          </template>
          <span class="font-semibold">Exporter l'image</span>
          <template #icon-right>
            <span class="ml-auto font-mono text-sm opacity-70"
              >{{ formatLabel }} {{ exportSize.width }} × {{ exportSize.height }}</span
            >
          </template>
        </AppButton>
      </div>

      <div class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <span class="text-sm font-medium tracking-widest text-gray-500 uppercase"
            >Lien court</span
          >
          <div class="flex items-center gap-2 rounded-xl border border-gray-200 p-2 pl-4">
            <span
              class="flex-1 min-w-0 truncate font-mono text-primary-900"
              data-cy="share-view-short-link"
              >{{ shortUrl || "Création du lien…" }}</span
            >
            <AppButton
              variant="gold"
              :disabled="!shortUrl"
              data-cy="share-view-copy-button"
              @click="handleCopy"
            >
              <template #icon-left>
                <IconCheck v-if="isCopied" :size="16" />
                <IconCopy v-else :size="16" />
              </template>
              {{ isCopied ? "Copié" : "Copier" }}
            </AppButton>
          </div>
        </div>

        <dl class="flex flex-col m-0" data-cy="share-view-details">
          <div
            v-for="detail in details"
            :key="detail.label"
            class="flex items-baseline justify-between gap-4 py-3 border-b border-gray-200"
          >
            <dt class="text-gray-500">{{ detail.label }}</dt>
            <dd class="m-0 text-right font-semibold text-gray-900">{{ detail.value }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </AppDialog>
</template>
