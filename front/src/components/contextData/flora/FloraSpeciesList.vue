<script lang="ts" setup>
import { computed } from "vue"
import type { TreeRecommendation } from "@/types/flora"

interface Props {
  recommendations: TreeRecommendation[]
}

const props = defineProps<Props>()

const sortedRecommendations = computed(() =>
  [...props.recommendations].sort((a, b) => b.score - a.score)
)

const ecosystemLabels: Record<string, string> = {
  co2: "CO₂",
  cooling: "Rafraîchissement",
  biodiversity: "Biodiversité"
}
</script>

<template>
  <div class="species-list">
    <div
      v-for="species in sortedRecommendations"
      :key="species.scientificName"
      class="species-card"
    >
      <div class="species-header">
        <div class="species-names">
          <span class="common-name">{{ species.commonName }}</span>
          <span class="scientific-name">{{ species.scientificName }}</span>
        </div>
        <div class="badges">
          <span v-if="species.inpnValidated" class="inpn-badge">INPN</span>
          <span v-if="species.isNative" class="native-badge">Indigène</span>
        </div>
      </div>

      <p class="species-description">{{ species.description }}</p>

      <details v-if="species.reasoning.length > 0" class="reasoning">
        <summary>Pourquoi cet arbre ici ?</summary>
        <ul class="reasoning-list">
          <li v-for="(reason, index) in species.reasoning" :key="index">{{ reason }}</li>
        </ul>
      </details>

      <div v-if="species.ecosystemHighlights.length > 0" class="ecosystem-tags">
        <span v-for="service in species.ecosystemHighlights" :key="service" class="ecosystem-tag">
          {{ ecosystemLabels[service] || service }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.species-list {
  @apply flex flex-col gap-2;
}

.species-card {
  @apply p-3 border border-gray-200 rounded-lg;
}

.species-header {
  @apply flex items-start justify-between gap-2;
}

.species-names {
  @apply flex flex-col;
}

.common-name {
  @apply text-sm font-semibold text-gray-900;
}

.scientific-name {
  @apply text-xs text-gray-400 italic;
}

.badges {
  @apply flex gap-1 shrink-0;
}

.inpn-badge {
  @apply px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded;
}

.native-badge {
  @apply px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 rounded;
}

.species-description {
  @apply text-xs text-gray-600 mt-2 mb-0;
}

.reasoning {
  @apply text-xs text-gray-400 mt-2;
}

.reasoning summary {
  @apply cursor-pointer hover:text-gray-600;
}

.reasoning-list {
  @apply mt-1 mb-0 pl-4 list-disc;
}

.reasoning-list li {
  @apply mt-0.5;
}

.ecosystem-tags {
  @apply flex flex-wrap gap-1 mt-2;
}

.ecosystem-tag {
  @apply px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded;
}
</style>
