<script lang="ts" setup>
interface ContextDataScoreHeaderProps {
  /** Short code shown in the colored swatch (e.g. "A", "62%") */
  swatchLabel: string
  swatchColor: string
  swatchTextColor?: string
  eyebrow: string
  title: string
}

withDefaults(defineProps<ContextDataScoreHeaderProps>(), {
  swatchTextColor: undefined
})
</script>

<template>
  <section class="score-header">
    <span
      class="score-header-swatch"
      :style="{ backgroundColor: swatchColor, color: swatchTextColor }"
      aria-hidden="true"
    >
      {{ swatchLabel }}
    </span>
    <span class="score-header-copy">
      <span class="score-header-eyebrow">{{ eyebrow }}</span>
      <span class="score-header-title">{{ title }}</span>
    </span>
  </section>
</template>

<style scoped>
@reference "@/styles/main.css";

.score-header {
  @apply flex w-72 max-w-full items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3;
  @apply min-h-20;
}

.score-header-swatch {
  @apply flex h-12 w-12 shrink-0 items-center justify-center rounded-lg;
  @apply text-sm font-bold tabular-nums;
}

.score-header-copy {
  @apply flex min-w-0 flex-col text-left;
}

.score-header-eyebrow {
  @apply text-xs font-medium text-gray-500;
}

.score-header-title {
  @apply line-clamp-3 text-sm font-semibold leading-snug text-gray-900;
  overflow-wrap: anywhere;
}
</style>
