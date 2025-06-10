<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="flex p-2 flex-wrap justify-center gap-2">
      <div v-for="(zone, index) in zones" :key="index" class="flex items-center gap-1">
        <div
          :style="{ backgroundColor: getZoneColor(zone) }"
          :class="[
            'w-4 h-7 rounded cursor-pointer hover:scale-110 hover:shadow-lg transition-all duration-200 ease-out transform relative',
            mapStore.isZoneFiltered(zone) ? 'ring-2 ring-primary-900 scale-105 shadow-md' : ''
          ]"
          :data-zone="zone"
          :title="`Zone LCZ ${zone} - ${getZoneDesc(zone)} - Cliquez pour ${mapStore.isZoneFiltered(zone) ? 'désactiver' : 'activer'} le filtre`"
          @click="handleZoneClick(zone)"
        >
          <!-- Indicateur de sélection -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-0"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-0"
          >
            <div
              v-if="mapStore.isZoneFiltered(zone)"
              class="absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full border border-white flex items-center justify-center"
            >
              <span class="text-white text-[8px] font-bold">✓</span>
            </div>
          </Transition>
        </div>
      </div>
    </div>
    <button class="text-lg flex flex-col items-center" @click="isExpanded = !isExpanded">
      <span class="text-sm">
        {{ isExpanded ? "Masquer les détails" : "Afficher les détails" }}
      </span>
      <span class="text-lg"> {{ isExpanded ? "▲" : "▼" }} </span>
    </button>
    <div v-if="isExpanded" class="flex flex-col items-start mt-2 gap-1">
      <div
        v-for="(zone, index) in zones"
        :key="'vertical-' + index"
        class="flex items-center gap-2"
      >
        <div
          :style="{ backgroundColor: getZoneColor(zone) }"
          :class="[
            'w-4 h-4 rounded cursor-pointer hover:scale-110 hover:shadow-lg transition-all duration-200 ease-out transform relative',
            mapStore.isZoneFiltered(zone) ? 'ring-2 ring-primary-900 scale-105 shadow-md' : ''
          ]"
          :data-zone="zone"
          :title="`Zone LCZ ${zone} - ${getZoneDesc(zone)} - Cliquez pour ${mapStore.isZoneFiltered(zone) ? 'désactiver' : 'activer'} le filtre`"
          @click="handleZoneClick(zone)"
        >
          <!-- Indicateur de sélection -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-0"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-0"
          >
            <div
              v-if="mapStore.isZoneFiltered(zone)"
              class="absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full border border-white flex items-center justify-center"
            >
              <span class="text-white text-[8px] font-bold">✓</span>
            </div>
          </Transition>
        </div>
        <span class="text-[0.9rem]">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"
import { useMapStore } from "@/stores/map"

const isExpanded = ref(false)
const mapStore = useMapStore()

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

const handleZoneClick = (zone: string) => {
  mapStore.toggleZoneFilter(zone)
}
</script>
