<script lang="ts" setup>
interface ContextDataSkeletonProps {
  rows?: number
}

withDefaults(defineProps<ContextDataSkeletonProps>(), {
  rows: 4
})
</script>

<template>
  <div class="skeleton" data-cy="context-data-skeleton" aria-hidden="true">
    <div class="skeleton-score"></div>
    <div class="skeleton-rows">
      <div v-for="n in rows" :key="n" class="skeleton-row"></div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.skeleton {
  @apply flex w-full flex-col gap-4 p-4;
}

.skeleton-score {
  @apply h-20 w-full rounded-xl bg-gray-100 animate-pulse;
}

.skeleton-rows {
  @apply flex flex-col gap-2;
}

.skeleton-row {
  @apply h-9 w-full rounded-md bg-gray-100 animate-pulse;
}

.skeleton-row:nth-child(2) {
  @apply w-5/6;
}

.skeleton-row:nth-child(4) {
  @apply w-4/6;
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-score,
  .skeleton-row {
    animation: none;
  }
}
</style>
