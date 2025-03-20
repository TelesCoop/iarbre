<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="flex p-2 flex-wrap justify-center gap-2">
      <div v-for="(zone, index) in zones" :key="index" class="flex items-center gap-1">
        <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(zone) }"></div>
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
        <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(zone) }"></div>
        <span class="text-[0.9rem]">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

const isExpanded = ref(false)

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

function getZoneDesc(zone: string): string {
  const descriptions: Record<string, string> = {
    1: "Ensemble compact de tours",
    2: "Ensemble compact d'immeubles",
    3: "Ensemble compact de maisons",
    4: "Ensemble de tours espacées",
    5: "Ensemble d'immeubles espacés",
    6: "Ensemble de maisons espacées",
    7: "Ensemble dense de constructions légères",
    8: "Bâtiments bas de grande emprise",
    9: "Implantation diffuse de maisons",
    A: "Espace densément arboré",
    B: "Ensemble arboré clairsemé",
    C: "Espace végétalisé hétérogène",
    D: "Végétation basse",
    E: "Sol imperméable naturel ou artificiel",
    F: "Sol nu perméable",
    G: "Surface en eau"
  }
  return descriptions[zone] || "Description non disponible"
}

function getZoneColor(zone: string): string {
  const colors: Record<string, string> = {
    1: "#8C0000",
    2: "#D10000",
    3: "#FF0000",
    4: "#BF4D00",
    5: "#fa6600",
    6: "#ff9955",
    7: "#faee05",
    8: "#bcbcbc",
    9: "#ffccaa",
    A: "#006a00",
    B: "#00aa00",
    C: "#648525",
    D: "#b9db79",
    E: "#fbf7ae",
    F: "#FBF7AE",
    G: "#6A6AFF"
  }
  return colors[zone] || "#CCCCCC"
}
</script>
