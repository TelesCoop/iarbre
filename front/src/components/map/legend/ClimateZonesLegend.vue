<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="flex p-2 flex-wrap justify-center gap-2">
      <div v-for="(zone, index) in zones" :key="index" class="flex items-center gap-1">
        <div :style="{ backgroundColor: getZoneColor(zone) }" class="w-4 h-7 rounded"></div>
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
        <div :style="{ backgroundColor: getZoneColor(zone) }" class="w-4 h-4 rounded"></div>
        <span class="text-[0.9rem]">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc, getZoneColor } from "@/utils/climateZones"

const isExpanded = ref(false)

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]
</script>
