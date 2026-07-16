<script lang="ts" setup>
import { computed } from "vue"
import type { VegetationData } from "@/types/vegetation"
import { getStrateShort, STRATE_CATEGORIES, STRATE_GRADIENT_CSS } from "@/utils/vegetation"

interface VegetationContextDataInfoProps {
  data: VegetationData
}

const props = defineProps<VegetationContextDataInfoProps>()

const dominantStrate = computed(() => getStrateShort(props.data.indice))
</script>

<template>
  <div class="strate-info vegestrate-panel">
    <div class="vegestrate-summary">
      <svg
        class="vegestrate-tree-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.4"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path
          d="M12 2.5c-3.4 0-6.1 2.6-6.1 5.9 0 2.9 2.1 5.3 4.9 5.8v6.4h2.4v-6.4c2.8-.5 4.9-2.9 4.9-5.8 0-3.3-2.7-5.9-6.1-5.9Z"
        />
      </svg>
      <div class="vegestrate-summary-main">
        <span class="vegestrate-summary-label">Strate dominante</span>
        <span class="text-3xl font-bold leading-none text-primary-800">{{ dominantStrate }}</span>
      </div>
      <p class="vegestrate-summary-aside">Classification par hauteur</p>
    </div>

    <div class="vegestrate-legend-card">
      <div class="vegestrate-scale-col" aria-hidden="true" />
      <div
        role="img"
        aria-label="Échelle des strates végétales, de la strate herbacée à la strate arborée"
        class="vegestrate-bar"
        :style="{ background: STRATE_GRADIENT_CSS }"
      />
      <ul class="vegestrate-categories">
        <li v-for="category in STRATE_CATEGORIES" :key="category.label" class="flex flex-col">
          <span class="vegestrate-category-label">{{ category.label }}</span>
          <span class="vegestrate-category-range">{{ category.range }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
