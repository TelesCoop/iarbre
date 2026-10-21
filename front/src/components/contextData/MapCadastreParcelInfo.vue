<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"

const mapStore = useMapStore()
const parcel = computed(() => mapStore.selectedCadastreParcel)

const formattedSurface = computed(() => {
  if (!parcel.value?.surface) return "N/A"
  return `${parcel.value.surface.toLocaleString("fr-FR")} m²`
})
</script>

<template>
  <MapFeatureInfoCard
    v-if="parcel"
    :title="`Parcelle ${parcel.section}${parcel.numero}`"
    :rows="[{ label: 'Surface', value: formattedSurface }]"
    data-cy="cadastre-parcel-info"
    @close="mapStore.clearCadastreSelection()"
  >
    <template #icon>
      <IconMap class="text-primary-500 shrink-0" :size="16" aria-hidden="true" />
    </template>
  </MapFeatureInfoCard>
</template>
