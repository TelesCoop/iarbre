<script lang="ts" setup>
import IconVegestrate from "@/components/icons/IconVegestrate.vue"
import { useMapStore } from "@/stores/map"
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

const props = defineProps<Props>()

const mapStore = useMapStore()

const filterStrate = (indice?: VegetationIndice) => {
  if (!props.filterable || !indice) return
  mapStore.toggleAndApplyFilter(indice)
}
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
          <component
            :is="filterable && category.indice ? 'button' : 'div'"
            :type="filterable && category.indice ? 'button' : undefined"
            :aria-pressed="
              filterable && category.indice ? mapStore.isFiltered(category.indice) : undefined
            "
            :aria-label="
              filterable && category.indice ? `${category.label} — cliquez pour filtrer` : undefined
            "
            :class="[
              'vegestrate-category',
              filterable && category.indice && mapStore.isFiltered(category.indice)
                ? 'is-selected'
                : '',
              filterable &&
              category.indice &&
              mapStore.hasActiveFilters &&
              !mapStore.isFiltered(category.indice)
                ? 'is-dimmed'
                : ''
            ]"
            @click="filterStrate(category.indice)"
          >
            <span class="vegestrate-category-label">{{ category.label }}</span>
            <span class="vegestrate-category-range">{{ category.range }}</span>
          </component>
        </li>
      </ul>
    </div>
  </div>
</template>
