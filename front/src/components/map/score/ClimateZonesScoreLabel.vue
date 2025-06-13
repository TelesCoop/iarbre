<script lang="ts" setup>
import { computed } from "vue"
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"
import { useMapStore } from "@/stores/map"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface Props {
  zone: string
  size: "compact" | "detailed"
}

const props = defineProps<Props>()
defineEmits<{
  click: [zone: string]
}>()

const mapStore = useMapStore()

const isFiltered = computed(() => mapStore.isFiltered(props.zone))

const zoneClasses = computed(() => [
  props.size === "compact" ? "w-4 h-7" : "w-4 h-4",
  isFiltered.value ? "ring-2 ring-primary-900 scale-105 shadow-md" : ""
])

const zoneTitle = computed(
  () =>
    `Zone LCZ ${props.zone} - ${getZoneDesc(props.zone)} - Cliquez pour ${isFiltered.value ? "désactiver" : "activer"} le filtre`
)
</script>

<template>
  <div
    :class="zoneClasses"
    :data-zone="zone"
    :style="{ backgroundColor: getZoneColor(zone) }"
    :title="zoneTitle"
    class="rounded cursor-pointer hover:scale-110 hover:shadow-lg transition-all duration-200 ease-out transform relative"
    @click="$emit('click', zone)"
  >
    <FilterIndicator :is-visible="isFiltered" />
  </div>
</template>
