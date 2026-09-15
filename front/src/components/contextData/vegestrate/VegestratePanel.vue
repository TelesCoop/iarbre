<script lang="ts" setup>
import IconVegestrate from "@/components/icons/IconVegestrate.vue"
import FilterableLegendItem from "@/components/map/legend/FilterableLegendItem.vue"
import type { VegetationIndice } from "@/types/vegetation"

interface Category {
  label: string
  range: string
  indice?: VegetationIndice
}

type ClassBinding = string | Record<string, boolean> | (string | Record<string, boolean>)[]

interface Props {
  summaryLabel: string
  asideNote: string
  barBackground: string
  barAriaLabel: string
  categories: Category[]
  barClass?: ClassBinding
  filterable?: boolean
}

defineProps<Props>()
</script>

<template>
  <div class="vegestrate-panel">
    <div class="vegestrate-summary">
      <IconVegestrate class="vegestrate-tree-icon" />
      <div class="vegestrate-summary-main">
        <span class="vegestrate-summary-label">{{ summaryLabel }}</span>
        <slot name="value" />
      </div>
      <p class="vegestrate-summary-aside">{{ asideNote }}</p>
    </div>

    <div class="vegestrate-legend-card">
      <div class="vegestrate-scale-col relative h-60 text-right" aria-hidden="true">
        <slot name="scale" />
      </div>
      <div
        role="img"
        :aria-label="barAriaLabel"
        :class="['vegestrate-bar relative', barClass]"
        :style="{ background: barBackground }"
      >
        <slot name="bar" />
      </div>
      <ul class="vegestrate-categories">
        <li v-for="category in categories" :key="category.label" class="flex">
          <FilterableLegendItem
            v-if="filterable && category.indice"
            :value="category.indice"
            :label="category.label"
            class="vegestrate-category"
          >
            <span class="vegestrate-category-label">{{ category.label }}</span>
            <span class="vegestrate-category-range">{{ category.range }}</span>
          </FilterableLegendItem>
          <div v-else class="vegestrate-category">
            <span class="vegestrate-category-label">{{ category.label }}</span>
            <span class="vegestrate-category-range">{{ category.range }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
