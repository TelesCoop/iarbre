<script lang="ts" setup>
import { computed, onBeforeUnmount, ref, watch } from "vue"
import AppDialog from "@/components/shared/AppDialog.vue"
import AppButton from "@/components/shared/AppButton.vue"
import IconCheck from "@/components/icons/IconCheck.vue"
import IconCopy from "@/components/icons/IconCopy.vue"
import IconImage from "@/components/icons/IconImage.vue"
import { fetchShortLink, useCopyLink } from "@/composables/useShortLink"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel, DataTypeToSourceDate, MapStyleToLabel } from "@/utils/enum"
import {
  EXPORT_HEIGHT_PX,
  EXPORT_WIDTH_PX,
  buildExportFileName,
  generateMapExport
} from "@/utils/mapExport"

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
const exportBlob = ref<Blob | null>(null)
const exportFileName = ref("")
const isGenerating = ref(false)
const hasExportError = ref(false)
const details = ref<ViewDetail[]>([])
let generationId = 0

const releasePreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ""
  exportBlob.value = null
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

const prepareShare = async () => {
  const currentId = ++generationId
  const map = mapStore.getMapInstance(props.mapId)
  const { lat, lng } = map.getCenter()
  const zoom = map.getZoom()
  details.value = snapshotDetails(lat, lng, zoom)
  exportFileName.value = `${buildExportFileName(mapStore.selectedDataType, lat, lng, zoom)}.png`
  shortUrl.value = ""
  hasExportError.value = false
  isGenerating.value = true
  releasePreview()

  fetchShortLink().then((url) => {
    if (currentId === generationId) shortUrl.value = url
  })

  try {
    const blob = await generateMapExport(
      map,
      DataTypeToLabel[mapStore.selectedDataType],
      document.querySelector<HTMLElement>(".legend-panel")
    )
    if (currentId !== generationId) return
    exportBlob.value = blob
    previewUrl.value = URL.createObjectURL(blob)
  } catch (error) {
    console.error(error)
    if (currentId === generationId) hasExportError.value = true
  } finally {
    if (currentId === generationId) isGenerating.value = false
  }
}

const downloadExport = () => {
  if (!previewUrl.value) return
  const link = document.createElement("a")
  link.href = previewUrl.value
  link.download = exportFileName.value
  link.click()
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
      releasePreview()
    }
  },
  { immediate: true }
)

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
          :style="{ aspectRatio: `${EXPORT_WIDTH_PX} / ${EXPORT_HEIGHT_PX}` }"
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

        <AppButton
          variant="gold"
          size="lg"
          full-width
          :disabled="!previewUrl"
          :loading="isGenerating"
          data-cy="share-view-export-button"
          @click="downloadExport"
        >
          <template #icon-left>
            <IconImage :size="20" />
          </template>
          <span class="font-semibold">Exporter l'image</span>
          <template #icon-right>
            <span class="ml-auto font-mono text-sm opacity-70"
              >PNG {{ EXPORT_WIDTH_PX }} × {{ EXPORT_HEIGHT_PX }}</span
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
