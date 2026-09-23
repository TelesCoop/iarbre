<script lang="ts" setup>
import { computed, onBeforeUnmount, ref, watch } from "vue"
import { Viewer } from "@photo-sphere-viewer/core"
import "@photo-sphere-viewer/core/index.css"
import { useMapStore } from "@/stores/map"
import { buildPanoramaxPictureUrl, formatPanoramaxDate } from "@/utils/panoramax"
import IconClose from "@/components/icons/IconClose.vue"
import IconPanoramax from "@/components/icons/IconPanoramax.vue"

const mapStore = useMapStore()

const picture = computed(() => mapStore.selectedPanoramaxPicture)
const canvasEl = ref<HTMLElement | null>(null)
let viewer: Viewer | null = null

const metaParts = computed(() =>
  [
    formatPanoramaxDate(picture.value?.datetime),
    picture.value?.producer,
    picture.value?.license
  ].filter((part): part is string => !!part)
)

const pictureUrl = computed(() => (picture.value ? buildPanoramaxPictureUrl(picture.value) : null))

const isFlat = computed(() => picture.value?.type === "flat")

// The sd derivate is ~0.4 MB against ~3 MB for hd, which decides whether a click opens.
const panoramaUrl = computed(
  () => picture.value?.assets?.sd ?? picture.value?.assets?.hd ?? picture.value?.assets?.thumb
)

const destroyViewer = () => {
  viewer?.destroy()
  viewer = null
}

watch(
  [panoramaUrl, canvasEl],
  async ([panorama, container]) => {
    if (!panorama || !container) {
      destroyViewer()
      return
    }

    if (!viewer) {
      viewer = new Viewer({
        container,
        panorama,
        navbar: false,
        loadingTxt: "Chargement…",
        touchmoveTwoFingers: false,
        mousewheelCtrlKey: false
      })
      return
    }

    try {
      await viewer.setPanorama(panorama)
    } catch (error) {
      console.error("Panoramax: could not display picture", error)
      destroyViewer()
      mapStore.clearPanoramaxSelection()
    }
  },
  { immediate: true, flush: "post" }
)

onBeforeUnmount(destroyViewer)
</script>

<template>
  <div
    v-if="picture"
    class="map-control flex flex-col overflow-hidden shadow-lg w-[28rem] max-w-[calc(100vw-1rem)]"
    data-cy="panoramax-viewer"
  >
    <div class="flex items-center justify-between gap-3 px-3 pt-3">
      <div class="flex items-center gap-2 min-w-0">
        <IconPanoramax class="shrink-0" :size="16" aria-hidden="true" />
        <span class="text-sm font-medium font-sans truncate">{{
          isFlat ? "Vue de rue" : "Vue immersive"
        }}</span>
      </div>
      <MapControlButton
        aria-label="Fermer"
        class="w-7 h-7 text-gray-400 hover:text-gray-600 hover:bg-gray-100 hover:border-gray-200"
        data-cy="panoramax-viewer-close"
        size="sm"
        @click="mapStore.clearPanoramaxSelection()"
      >
        <IconClose :size="12" />
      </MapControlButton>
    </div>

    <img
      v-if="isFlat"
      alt="Photo de rue Panoramax"
      class="mt-2 h-60 w-full object-contain bg-gray-900"
      data-cy="panoramax-flat-image"
      :src="panoramaUrl"
    />
    <div v-else ref="canvasEl" class="mt-2 h-60 bg-gray-900" data-cy="panoramax-canvas"></div>

    <div
      class="flex flex-wrap items-center gap-x-2 gap-y-1 px-3 py-2 text-xs font-sans text-gray-500 border-t border-gray-100"
    >
      <template v-for="(part, index) in metaParts" :key="part">
        <span v-if="index > 0" class="text-gray-300">·</span>
        <span>{{ part }}</span>
      </template>
      <a
        v-if="pictureUrl"
        class="ml-auto font-medium text-primary-500 underline"
        data-cy="panoramax-picture-link"
        :href="pictureUrl"
        rel="noopener"
        target="_blank"
      >
        Voir sur Panoramax ↗
      </a>
    </div>
  </div>
</template>
