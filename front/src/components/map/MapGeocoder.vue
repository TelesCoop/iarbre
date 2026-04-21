<script lang="ts" setup>
import { ref, computed, onUnmounted } from "vue"
import { useDebounceFn, onClickOutside } from "@vueuse/core"
import maplibregl from "maplibre-gl"
import { fetchGeocode, ZOOM_BY_TYPE, type GeocoderFeature } from "@/utils/geocoder"
import { useMapStore } from "@/stores/map"
import AppSpinner from "@/components/shared/AppSpinner.vue"

const mapStore = useMapStore()

const wrapperRef = ref<HTMLElement>()
const query = ref("")
const results = ref<GeocoderFeature[]>([])
const loading = ref(false)
const focused = ref(false)
const activeIndex = ref(-1)
let searchMarker: maplibregl.Marker | null = null

const PULSE_BASE = "absolute inset-0 m-auto w-[1.125rem] h-[1.125rem] rounded-full bg-primary-500"

const createDiv = (...classes: string[]): HTMLDivElement => {
  const el = document.createElement("div")
  el.className = classes.join(" ")
  return el
}

const createPulseElement = (): HTMLElement => {
  const el = createDiv("relative w-12 h-12")
  el.append(
    createDiv(PULSE_BASE, "border-[0.1875rem] border-white z-[1]"),
    createDiv(PULSE_BASE, "opacity-35 [animation:geocoder-pulse_2s_ease-out_infinite]"),
    createDiv(
      PULSE_BASE,
      "opacity-35 [animation:geocoder-pulse_2s_ease-out_infinite] [animation-delay:0.7s]"
    )
  )
  return el
}

const isOpen = computed(() => focused.value && results.value.length > 0)

const search = useDebounceFn(async () => {
  if (query.value.trim().length < 2) {
    results.value = []
    return
  }
  loading.value = true
  try {
    results.value = await fetchGeocode(query.value)
    activeIndex.value = -1
  } finally {
    loading.value = false
  }
}, 250)

const selectResult = (feature: GeocoderFeature) => {
  query.value = feature.name
  results.value = []
  focused.value = false

  const map = mapStore.getMapInstance("default")
  if (!map) return

  searchMarker?.remove()
  searchMarker = new maplibregl.Marker({ element: createPulseElement(), anchor: "center" })
    .setLngLat(feature.center)
    .addTo(map)

  map.flyTo({
    center: feature.center,
    zoom: ZOOM_BY_TYPE[feature.type] ?? 15
  })
}

const clear = () => {
  query.value = ""
  results.value = []
  searchMarker?.remove()
  searchMarker = null
}

const handleKeydown = (e: KeyboardEvent) => {
  if (!isOpen.value) return
  if (e.key === "ArrowDown") {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, results.value.length - 1)
  } else if (e.key === "ArrowUp") {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, -1)
  } else if (e.key === "Enter" && activeIndex.value >= 0) {
    e.preventDefault()
    selectResult(results.value[activeIndex.value])
  } else if (e.key === "Escape") {
    results.value = []
    focused.value = false
  }
}

onClickOutside(wrapperRef, () => {
  results.value = []
  focused.value = false
})

onUnmounted(() => {
  searchMarker?.remove()
})
</script>

<template>
  <div ref="wrapperRef" class="relative w-full lg:w-60" data-cy="map-geocoder">
    <div
      :class="[
        'flex items-center gap-1.5 px-2 py-1.5 lg:px-3 lg:py-2',
        'bg-white border rounded-lg transition-all duration-200',
        isOpen
          ? 'border-primary-300 border-b-gray-100 rounded-b-none'
          : focused
            ? 'border-primary-300'
            : 'border-gray-200'
      ]"
    >
      <svg
        class="w-3 h-3 lg:w-4 lg:h-4 shrink-0 text-gray-400"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" stroke-linecap="round" />
      </svg>
      <input
        v-model="query"
        aria-label="Rechercher une adresse"
        autocomplete="off"
        class="geocoder-input flex-1 min-w-0 bg-transparent border-none outline-none text-xs font-sans font-medium text-gray-700"
        placeholder="Recherche"
        type="search"
        @focus="focused = true"
        @input="search"
        @keydown="handleKeydown"
      />
      <AppSpinner v-if="loading" class="w-3.5 h-3.5 shrink-0 text-primary-500" />
      <button
        v-else-if="query"
        aria-label="Effacer"
        class="flex items-center justify-center shrink-0 w-4 h-4 rounded text-gray-400 bg-transparent border-none cursor-pointer transition-colors hover:text-gray-700 hover:bg-gray-100"
        type="button"
        @click="clear"
      >
        <svg
          fill="none"
          height="10"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-width="2.5"
          viewBox="0 0 14 14"
          width="10"
        >
          <path d="M1 1L13 13M1 13L13 1" />
        </svg>
      </button>
    </div>

    <Transition name="geocoder-dropdown">
      <ul
        v-if="isOpen"
        class="absolute left-0 right-0 z-50 bg-white border border-primary-300 border-t-0 rounded-b-lg shadow-lg overflow-hidden overflow-y-auto m-0 p-0 list-none max-h-80"
        role="listbox"
      >
        <li
          v-for="(result, i) in results"
          :key="result.id"
          :aria-selected="i === activeIndex"
          :data-active="i === activeIndex"
          class="group flex items-start gap-2.5 px-3 py-2.5 cursor-pointer transition-colors duration-100 border-b border-gray-100 last:border-b-0 hover:bg-primary-500 data-[active=true]:bg-primary-500"
          role="option"
          @mousemove="activeIndex = i"
          @mousedown.prevent="selectResult(result)"
        >
          <svg
            class="w-4 h-4 shrink-0 mt-0.5 transition-colors text-gray-400 group-hover:text-white group-data-[active=true]:text-white"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          <div class="flex flex-col min-w-0">
            <span
              class="text-sm font-medium transition-colors text-gray-900 group-hover:text-white group-data-[active=true]:text-white"
            >
              {{ result.name }}
            </span>
            <span
              v-if="result.address"
              class="text-xs transition-colors truncate text-gray-500 group-hover:text-white/80 group-data-[active=true]:text-white/80"
            >
              {{ result.address }}
            </span>
          </div>
        </li>
      </ul>
    </Transition>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.geocoder-input::-webkit-search-cancel-button {
  display: none;
}

.geocoder-input::placeholder {
  @apply text-xs font-medium text-gray-500 uppercase tracking-tight;
}

.geocoder-dropdown-enter-active,
.geocoder-dropdown-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.geocoder-dropdown-enter-from,
.geocoder-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-0.25rem);
}
</style>

<style>
@keyframes geocoder-pulse {
  0% {
    transform: scale(1);
    opacity: 0.35;
  }
  100% {
    transform: scale(3);
    opacity: 0;
  }
}
</style>
