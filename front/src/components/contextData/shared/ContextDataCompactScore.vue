<script lang="ts" setup>
interface ContextDataCompactScoreProps {
  label: string
  value: string
  color?: string
}

withDefaults(defineProps<ContextDataCompactScoreProps>(), {
  color: undefined
})
</script>

<template>
  <div class="compact-score" data-cy="context-data-score-compact">
    <span class="compact-label">{{ label }}</span>
    <span class="compact-value" :style="color ? { color } : undefined">{{ value }}</span>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.compact-score {
  @apply flex flex-col items-center justify-center gap-0.5;
  @apply min-w-24 px-4 py-2 rounded-lg border border-gray-200 bg-gray-50;
}

.compact-label {
  @apply text-2xs font-medium uppercase tracking-wide text-gray-500;
}

.compact-value {
  @apply text-lg font-bold leading-none tabular-nums text-gray-800;
}
</style>
