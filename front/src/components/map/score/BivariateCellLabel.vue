<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface BivariateCellLabelProps {
  plantability: number
  vulnerability: number
  color: string
  highlighted?: boolean
  clickable?: boolean
}

const props = defineProps<BivariateCellLabelProps>()
defineEmits<{
  click: []
}>()

const mapStore = useMapStore()

const isHighlighted = computed(() => props.highlighted ?? false)
const cellId = computed(() => `${props.plantability}-${props.vulnerability}`)
const isFiltered = computed(() => mapStore.isFiltered(cellId.value))

const cellClasses = computed(() => [
  "relative",
  isHighlighted.value ? "ring-2 ring-blue-500" : "",
  isFiltered.value ? "border-2 border-primary-900 shadow-md" : "",
  props.clickable
    ? "cursor-pointer hover:scale-110 hover:shadow-lg transition-all duration-200 ease-out transform"
    : ""
])

const cellTitle = computed(() =>
  props.clickable
    ? `Plantabilité: ${props.plantability}, Vulnérabilité: ${props.vulnerability} - Cliquez pour ${isFiltered.value ? "désactiver" : "activer"} le filtre`
    : undefined
)
</script>

<template>
  <div
    :class="cellClasses"
    :style="{ backgroundColor: props.color }"
    :title="cellTitle"
    style="width: 15px; height: 15px"
    @click="clickable ? $emit('click') : undefined"
  >
    <FilterIndicator :is-visible="isFiltered" />
  </div>
</template>
