<script lang="ts" setup>
import { computed, ref } from "vue"
import ContextDataFactorRow from "@/components/contextData/shared/ContextDataFactorRow.vue"
import VulnerabilityContextDataScoreBadge from "@/components/contextData/vulnerability/VulnerabilityContextDataScoreBadge.vue"
import type { ContextDataFactorGroup, ContextDataColorScheme } from "@/types/contextData"
import type { VulnerabilityCategory } from "@/utils/enum"
import { VulnerabilityMode } from "@/utils/vulnerability"

interface ContextDataAccordionItemProps {
  group: ContextDataFactorGroup
  colorScheme?: ContextDataColorScheme
  variant?: "cards" | "diagnostic"
  getCategoryScore?: (category: VulnerabilityCategory, mode: VulnerabilityMode) => number | null
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
}

const props = withDefaults(defineProps<ContextDataAccordionItemProps>(), {
  colorScheme: "plantability",
  variant: "cards",
  getCategoryScore: undefined,
  getScoreColor: undefined,
  getScoreLabel: undefined
})

const isVulnerabilityGroup = computed(() => {
  return props.colorScheme === "vulnerability" && props.getCategoryScore !== undefined
})

const vulnerabilityCategory = computed(() => {
  if (!isVulnerabilityGroup.value) return null
  return props.group?.category as VulnerabilityCategory
})

const isExpanded = ref(false)

const sectionClasses = computed(() => [
  "data-section",
  `data-section--${props.variant}`,
  `data-section--${props.colorScheme}`
])

const factorCountLabel = computed(() => {
  const count = props.group.factors.length
  return `${count} indicateur${count > 1 ? "s" : ""}`
})

const impactLabel = computed(() => {
  if (props.group.hasNegativeImpact) return "Contrainte"
  if (props.group.hasPositiveImpact) return "Favorable"
  return null
})

const impactToneClass = computed(() => {
  if (props.group.hasNegativeImpact) return "section-tone--negative"
  if (props.group.hasPositiveImpact) return "section-tone--positive"
  return "section-tone--neutral"
})

const toggle = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div :data-cy="`category-${group?.category}`" :class="sectionClasses" role="listitem">
    <button
      :aria-expanded="isExpanded"
      class="section-header accordion-header"
      type="button"
      @click="toggle"
    >
      <span class="section-leading">
        <span class="section-copy">
          <span class="section-title">{{ group.label }}</span>
          <span class="section-meta">{{ factorCountLabel }}</span>
        </span>
      </span>
      <span
        v-if="variant === 'diagnostic' && impactLabel"
        :class="['section-tone', impactToneClass]"
      >
        {{ impactLabel }}
      </span>
      <span
        v-if="isVulnerabilityGroup && vulnerabilityCategory && getCategoryScore"
        class="section-score-badges"
      >
        <VulnerabilityContextDataScoreBadge
          :category="vulnerabilityCategory"
          :get-category-score="getCategoryScore"
        />
      </span>
      <svg
        :class="['section-chevron', { collapsed: !isExpanded }]"
        fill="none"
        height="10"
        viewBox="0 0 12 12"
        width="10"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 4L6 8L10 4"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
        />
      </svg>
    </button>

    <div v-show="isExpanded" class="section-body">
      <div class="section-body-inner">
        <div v-if="variant === 'diagnostic'" class="factor-list vulnerability-list">
          <div class="vulnerability-heading" aria-hidden="true">
            <span></span>
            <span></span>
            <span>Jour</span>
            <span>Nuit</span>
          </div>
          <ContextDataFactorRow
            v-for="factor in group.factors"
            :key="factor.key"
            :factor="factor"
            variant="vulnerability"
            :get-score-color="getScoreColor"
            :get-score-label="getScoreLabel"
          />
        </div>

        <div v-else class="factor-list">
          <ContextDataFactorRow
            v-for="factor in group.factors"
            :key="factor.key"
            :factor="factor"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

/* ── Section container ── */

.data-section {
  @apply rounded-xl border border-gray-200 bg-white;
}

.data-section--cards {
  @apply bg-white;
}

.data-section--diagnostic {
  @apply bg-white;
}

/* ── Section header ── */

.section-header {
  @apply grid items-center gap-3 w-full px-4 py-3;
  @apply cursor-pointer transition-colors duration-200 hover:bg-gray-50;
  @apply text-left;
  @apply bg-white rounded-xl;
  grid-template-columns: minmax(0, 1fr) auto auto;
}

.section-header[aria-expanded="true"] {
  @apply rounded-b-none;
}

.data-section--cards .section-header {
  @apply min-h-16;
}

.data-section--diagnostic .section-header {
  @apply bg-white;
}

.section-leading {
  @apply flex items-center gap-3 min-w-0 flex-1;
}

.section-icon {
  @apply flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-base leading-none;
  @apply text-primary-500 border border-gray-100;
}

.section-copy {
  @apply flex min-w-0 flex-col;
}

.section-title {
  @apply truncate text-sm font-semibold text-gray-900 normal-case;
}

.section-meta {
  @apply text-xs font-normal text-gray-500 mt-0.5;
}

.section-tone {
  @apply hidden xs:inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium;
  @apply whitespace-nowrap;
}

.section-tone--positive {
  @apply border-primary-200 bg-primary-100 text-primary-700;
}

.section-tone--negative {
  @apply border-orange-200 bg-orange-100 text-orange-700;
}

.section-tone--neutral {
  @apply border-gray-200 bg-gray-100 text-gray-700;
}

.section-score-badges {
  @apply flex items-center gap-1;
}

.section-chevron {
  @apply text-gray-400;
}

.section-chevron.collapsed {
  transform: rotate(-90deg);
}

/* ── Animated body ── */

.section-body-inner {
  @apply overflow-visible;
}

.data-section--cards .section-body-inner {
  @apply bg-white px-4 pb-4 rounded-b-xl;
}

.data-section--diagnostic .section-body-inner {
  @apply bg-white px-4 pb-4 rounded-b-xl;
}

/* ── Factor list ── */

.factor-list {
  @apply flex flex-col gap-3;
}

.vulnerability-heading {
  @apply grid items-center gap-x-2 text-xs;
  grid-template-columns: 0.5rem minmax(0, 1fr) 2.5rem 2.5rem;
}

.vulnerability-heading {
  @apply text-center text-xs font-medium text-gray-400;
}
</style>
