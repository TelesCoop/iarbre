<template>
  <div data-cy="lcz-score-popup" class="p-2.5 max-w-xs flex flex-wrap gap-2">
    <div class="flex items-center gap-2 w-full">
      <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(index) }"></div>
      <span class="text-[0.9rem]">LCZ {{ index }}</span>
    </div>
    <div class="w-full">
      <span class="text-[0.9rem]">{{ getZoneDesc(index) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  index: {
    required: true,
    type: String
  }
})

function getZoneColor(zone: string): string {
  const colors: Record<string, string> = {
    "1": "#8C0000",
    "2": "#D10000",
    "3": "#FF0000",
    "4": "#BF4D00",
    "5": "#fa6600",
    "6": "#ff9955",
    "7": "#faee05",
    "8": "#bcbcbc",
    "9": "#ffccaa",
    A: "#006a00",
    B: "#00aa00",
    C: "#648525",
    D: "#b9db79",
    E: "#000000",
    F: "#FBF7AE",
    G: "#6A6AFF"
  }
  return colors[zone] || "#CCCCCC"
}

function getZoneDesc(zone: string): string {
  const descriptions: Record<string, string> = {
    "1": "Ensemble compact de tours",
    "2": "Ensemble compact d'immeubles",
    "3": "Ensemble compact de maisons",
    "4": "Ensemble de tours espacées",
    "5": "Ensemble d'immeubles espacés",
    "6": "Ensemble de maisons espacées",
    "7": "Ensemble dense de constructions légères",
    "8": "Bâtiments bas de grande emprise",
    "9": "Implantation diffuse de maisons",
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
</script>
