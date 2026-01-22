<script lang="ts" setup>
import { computed } from "vue"
import { getZoneDesc, getZoneColor } from "@/utils/climateZone"
import { useMapStore } from "@/stores/map"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface Props {
  zone: string
  size: "compact" | "detailed"
  isFirst?: boolean
  isLast?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  click: [zone: string]
}>()

const mapStore = useMapStore()

const isFiltered = computed(() => mapStore.isFiltered(props.zone))

const zoneClasses = computed(() => [
  props.size === "compact" ? "h-7" : "h-4",
  isFiltered.value ? "border-2 border-primary-900 " : "",
  props.isFirst ? "rounded-l-sm" : "",
  props.isLast ? "rounded-r-sm" : ""
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
    class="cursor-pointer hover:scale-110 hover: transition-all duration-200 ease-out transform relative"
    style="width: 0.9375rem"
    @click="$emit('click', zone)"
  >
    <FilterIndicator :is-visible="isFiltered" />
  </div>
</template>
