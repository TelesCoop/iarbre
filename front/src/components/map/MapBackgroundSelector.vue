<script lang="ts" setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue"
import { useMapStore } from "@/stores/map"
import { MapStyle } from "@/utils/enum"
import { MAP_STYLE_OPTIONS, getMapStyleOption } from "@/utils/mapStyleOptions"
import IconInfo from "@/components/icons/IconInfo.vue"

const mapStore = useMapStore()
const isExpanded = ref(false)
const isSourceOpen = ref(false)
const wrapperRef = ref<HTMLElement | null>(null)

const options = MAP_STYLE_OPTIONS

const currentStyle = computed(() => mapStore.selectedMapStyle)

const currentOption = computed(() => getMapStyleOption(currentStyle.value))

const currentSource = computed(() => currentOption.value.source)

const isSelected = (style: MapStyle): boolean => currentStyle.value === style

const handleSelectStyle = (style: MapStyle) => {
  mapStore.changeMapStyle(style)
  isExpanded.value = false
  isSourceOpen.value = false
}

const handleToggleExpanded = () => {
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    isSourceOpen.value = false
  }
}

const handleToggleSource = () => {
  isSourceOpen.value = !isSourceOpen.value
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key !== "Escape") return
  if (isSourceOpen.value) {
    isSourceOpen.value = false
  } else if (isExpanded.value) {
    isExpanded.value = false
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (!isSourceOpen.value) return
  const target = event.target as Node | null
  if (target && wrapperRef.value && !wrapperRef.value.contains(target)) {
    isSourceOpen.value = false
  }
}

// Close the popover whenever the user picks a different background.
watch(currentStyle, () => {
  isSourceOpen.value = false
})

onMounted(() => {
  document.addEventListener("click", handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside)
})
</script>

<template>
  <div ref="wrapperRef" class="bg-selector-wrapper" @keydown="handleKeydown">
    <div :class="['bg-selector-container', { expanded: isExpanded }]">
      <div class="bg-selector-toggle-wrapper">
        <button
          :aria-expanded="isExpanded"
          aria-controls="bg-selector-options"
          aria-label="Sélectionner le fond de carte"
          class="bg-selector-toggle"
          data-cy="bg-selector-toggle"
          type="button"
          @click="handleToggleExpanded"
        >
          <div class="bg-selector-toggle-preview">
            <img :alt="currentOption.label" :src="currentOption.image" class="preview-image" />
          </div>
          <span class="bg-selector-toggle-label">{{ currentOption.label }}</span>
        </button>

        <button
          :aria-expanded="isSourceOpen"
          aria-label="Afficher la source du fond de carte"
          class="bg-selector-info-button"
          data-cy="bg-selector-info-button"
          type="button"
          @click="handleToggleSource"
        >
          <IconInfo :size="14" />
        </button>

        <div
          v-if="isSourceOpen"
          class="bg-selector-source-popover"
          data-cy="bg-selector-source-popover"
          role="dialog"
        >
          <div class="bg-selector-source-title">Source</div>
          <div class="bg-selector-source-content">
            <a
              v-if="currentSource.url"
              :href="currentSource.url"
              class="bg-selector-source-link"
              rel="noopener"
              target="_blank"
            >
              {{ currentSource.provider }}
            </a>
            <span v-else>{{ currentSource.provider }}</span>
            <template v-if="currentSource.year"> — {{ currentSource.year }}</template>
          </div>
        </div>
      </div>

      <div
        id="bg-selector-options"
        :class="['bg-selector-options', { 'is-expanded': isExpanded }]"
        aria-label="Options de fond de carte"
        role="listbox"
      >
        <MapStyleOption
          v-for="option in options"
          :key="option.value"
          :data-cy="`bg-option-${option.value}`"
          :image="option.image"
          :label="option.label"
          :selected="isSelected(option.value)"
          :value="option.value"
          @select="handleSelectStyle"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.bg-selector-wrapper {
  @apply flex flex-col gap-2;
}

.bg-selector-container {
  @apply flex items-center;
  @apply bg-white rounded-lg;
  @apply border border-gray-200;
  padding: 10px;
  height: 90px;
}

.bg-selector-toggle-wrapper {
  @apply relative flex items-center;
  height: 100%;
}

.bg-selector-info-button {
  @apply absolute flex items-center justify-center;
  @apply rounded-full bg-white border border-gray-200 text-gray-500;
  @apply cursor-pointer transition-all;
  @apply hover:text-primary-500 hover:border-primary-300;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300;
  top: -0.35rem;
  right: -0.35rem;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
}

.bg-selector-source-popover {
  @apply absolute bg-white border border-gray-200 rounded-lg shadow-md;
  @apply font-sans text-xs text-gray-700;
  bottom: calc(100% + 0.5rem);
  left: 0;
  z-index: 40;
  padding: 0.5rem 0.75rem;
  min-width: 14rem;
  max-width: 20rem;
}

.bg-selector-source-title {
  @apply text-2xs font-semibold uppercase tracking-wide text-gray-500;
  margin-bottom: 0.25rem;
}

.bg-selector-source-content {
  @apply text-sm text-gray-800;
  line-height: 1.3;
}

.bg-selector-source-link {
  @apply text-primary-500 underline;
}

.bg-selector-source-link:hover {
  @apply text-primary-600;
}

.bg-selector-toggle {
  @apply flex flex-col items-center gap-2;
  @apply cursor-pointer transition-all;
  @apply hover:bg-gray-50 rounded-lg;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300;
  background: transparent;
  border: none;
  height: 100%;
}

.bg-selector-toggle-preview {
  @apply w-12 h-12 rounded flex items-center justify-center;
  @apply bg-gray-100;
  overflow: hidden;
  flex-shrink: 0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bg-selector-toggle-label {
  @apply text-xs font-sans text-gray-700 font-medium;
}

@media (min-width: 1024px) {
  .bg-selector-toggle-label {
    @apply text-sm;
  }
}

.bg-selector-options {
  @apply flex items-center gap-2 pl-2 ml-2;
  @apply border-l border-gray-200;
  @apply transition-all duration-300 ease-out;
  height: 100%;
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  padding-left: 0;
  margin-left: 0;
  border-left-width: 0;
}

.bg-selector-options.is-expanded {
  max-width: 25rem;
  opacity: 1;
  padding-left: 0.5rem;
  margin-left: 1.5rem;
  border-left-width: 1px;
}
</style>
