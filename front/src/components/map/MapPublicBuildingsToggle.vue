<script lang="ts" setup>
import { ref } from "vue"
import { useTapOutside } from "@/composables/useTapOutside"
import { useMapStore } from "@/stores/map"
import { ALL_PUBLIC_BUILDING_CATEGORIES, PublicBuildingCategoryToLabel } from "@/utils/enum"
import { PUBLIC_BUILDING_COLORS } from "@/utils/mapLayers"
import IconPublicBuilding from "@/components/icons/IconPublicBuilding.vue"
import IconChevron from "@/components/icons/IconChevron.vue"

const mapStore = useMapStore()
const isExpanded = ref(false)
const wrapperRef = ref<HTMLElement | null>(null)

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape") isExpanded.value = false
}

useTapOutside(wrapperRef, () => {
  isExpanded.value = false
})
</script>

<template>
  <div ref="wrapperRef" class="relative flex items-center" @keydown="handleKeydown">
    <div
      :class="['layer-chip !p-0 overflow-hidden', { active: mapStore.showPublicBuildingsLayer }]"
    >
      <button
        class="flex items-center gap-1.5 py-1.5 pl-3 pr-2 cursor-pointer"
        data-cy="public-buildings-toggle"
        type="button"
        @click="mapStore.togglePublicBuildingsLayer()"
      >
        <IconPublicBuilding class="layer-chip__icon" :size="14" />
        Bâtiments publics
      </button>
      <button
        :aria-expanded="isExpanded"
        aria-controls="public-buildings-categories"
        aria-label="Filtrer les catégories de bâtiments publics"
        class="flex items-center self-stretch pl-1.5 pr-2.5 border-l border-current/20 cursor-pointer"
        data-cy="public-buildings-categories-toggle"
        type="button"
        @click="isExpanded = !isExpanded"
      >
        <IconChevron :direction="isExpanded ? 'down' : 'up'" :size="12" />
      </button>
    </div>

    <div
      v-if="isExpanded"
      id="public-buildings-categories"
      class="map-popover flex flex-col min-w-48"
      data-cy="public-buildings-categories"
      role="group"
      aria-label="Catégories de bâtiments publics"
    >
      <label
        v-for="category in ALL_PUBLIC_BUILDING_CATEGORIES"
        :key="category"
        :data-cy="`public-buildings-category-${category}`"
        class="flex items-center gap-2 py-1 cursor-pointer text-xs font-sans text-gray-700"
      >
        <input
          :checked="mapStore.selectedPublicBuildingCategories.includes(category)"
          class="accent-primary-500 cursor-pointer"
          type="checkbox"
          @change="mapStore.togglePublicBuildingCategory(category)"
        />
        <span
          :style="{ backgroundColor: PUBLIC_BUILDING_COLORS[category] }"
          class="w-2.5 h-2.5 rounded-full shrink-0"
          aria-hidden="true"
        />
        {{ PublicBuildingCategoryToLabel[category] }}
      </label>
    </div>
  </div>
</template>
