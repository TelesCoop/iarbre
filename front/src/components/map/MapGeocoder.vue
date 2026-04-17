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

const createPulseElement = (): HTMLElement => {
  const el = document.createElement("div")
  el.className = "geocoder-pulse"
  el.innerHTML = `<div class="geocoder-pulse__dot"></div><div class="geocoder-pulse__ring"></div><div class="geocoder-pulse__ring"></div>`
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
  <div ref="wrapperRef" class="geocoder-wrapper" data-cy="map-geocoder">
    <div class="geocoder-input-row" :class="{ open: isOpen, focused }">
      <svg
        class="geocoder-search-icon"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" stroke-linecap="round" />
      </svg>
      <input
        v-model="query"
        class="geocoder-input"
        placeholder="Recherche"
        autocomplete="off"
        type="search"
        aria-label="Rechercher une adresse"
        @input="search"
        @focus="focused = true"
        @keydown="handleKeydown"
      />
      <AppSpinner v-if="loading" class="geocoder-spinner" />
      <button
        v-else-if="query"
        type="button"
        class="geocoder-clear"
        aria-label="Effacer"
        @click="clear"
      >
        <svg
          width="10"
          height="10"
          viewBox="0 0 14 14"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        >
          <path d="M1 1L13 13M1 13L13 1" />
        </svg>
      </button>
    </div>

    <Transition name="geocoder-dropdown">
      <ul v-if="isOpen" class="geocoder-results" role="listbox">
        <li
          v-for="(result, i) in results"
          :key="result.id"
          class="geocoder-result"
          :class="{ active: i === activeIndex }"
          role="option"
          :aria-selected="i === activeIndex"
          @mousedown.prevent="selectResult(result)"
          @mousemove="activeIndex = i"
        >
          <svg
            class="geocoder-pin"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          <div class="geocoder-result-text">
            <span class="geocoder-result-name">{{ result.name }}</span>
            <span v-if="result.address" class="geocoder-result-address">{{ result.address }}</span>
          </div>
        </li>
      </ul>
    </Transition>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.geocoder-wrapper {
  @apply relative w-full;
}

@media (min-width: 1024px) {
  .geocoder-wrapper {
    width: 240px;
  }
}

.geocoder-input-row {
  @apply flex items-center gap-1.5 px-2 py-1.5;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply transition-all duration-200;
}

@media (min-width: 1024px) {
  .geocoder-input-row {
    @apply px-3 py-2;
  }
}

.geocoder-input-row.focused,
.geocoder-input-row.open {
  @apply border-primary-300 ring-2 ring-primary-100;
}

.geocoder-input-row.open {
  @apply rounded-b-none border-b-gray-100;
}

.geocoder-search-icon {
  @apply w-3 h-3 shrink-0 text-gray-400;
}

@media (min-width: 1024px) {
  .geocoder-search-icon {
    @apply w-4 h-4;
  }
}

.geocoder-input {
  @apply flex-1 min-w-0 bg-transparent border-none outline-none;
  @apply text-xs font-sans font-medium text-gray-700;
}

.geocoder-input::placeholder {
  @apply text-xs font-medium text-gray-500 uppercase tracking-tight;
}

/* Remove native search cancel button */
.geocoder-input::-webkit-search-cancel-button {
  display: none;
}

.geocoder-clear {
  @apply flex items-center justify-center shrink-0;
  @apply w-4 h-4 rounded text-gray-400;
  @apply bg-transparent border-none cursor-pointer transition-colors;
}

.geocoder-clear:hover {
  @apply text-gray-700 bg-gray-100;
}

.geocoder-spinner {
  @apply w-3.5 h-3.5 shrink-0 text-primary-500;
}

.geocoder-results {
  @apply absolute left-0 right-0 z-50;
  @apply bg-white border border-primary-300 border-t-0 rounded-b-lg;
  @apply shadow-lg overflow-hidden overflow-y-auto;
  @apply m-0 p-0 list-none;
  max-height: 20rem;
}

.geocoder-result {
  @apply flex items-start gap-2.5 px-3 py-2.5 cursor-pointer;
  @apply transition-colors duration-100;
  @apply border-b border-gray-100 last:border-b-0;
}

.geocoder-result:hover,
.geocoder-result.active {
  @apply bg-primary-500;
}

.geocoder-pin {
  @apply w-4 h-4 shrink-0 mt-0.5 text-gray-400 transition-colors;
}

.geocoder-result:hover .geocoder-pin,
.geocoder-result.active .geocoder-pin {
  @apply text-white;
}

.geocoder-result-text {
  @apply flex flex-col min-w-0;
}

.geocoder-result-name {
  @apply text-sm font-medium text-gray-900 transition-colors;
}

.geocoder-result:hover .geocoder-result-name,
.geocoder-result.active .geocoder-result-name {
  @apply text-white;
}

.geocoder-result-address {
  @apply text-xs text-gray-500 transition-colors truncate;
}

.geocoder-result:hover .geocoder-result-address,
.geocoder-result.active .geocoder-result-address {
  @apply text-white/80;
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
  transform: translateY(-4px);
}
</style>

<style>
.geocoder-pulse {
  position: relative;
  width: 48px;
  height: 48px;
}

.geocoder-pulse__dot {
  position: absolute;
  inset: 0;
  margin: auto;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #426a45;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  z-index: 1;
}

.geocoder-pulse__ring {
  position: absolute;
  inset: 0;
  margin: auto;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #426a45;
  opacity: 0.35;
  animation: geocoder-pulse 2s ease-out infinite;
}

.geocoder-pulse__ring:nth-child(3) {
  animation-delay: 0.7s;
}

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
