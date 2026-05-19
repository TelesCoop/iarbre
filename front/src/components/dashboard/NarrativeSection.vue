<script lang="ts" setup>
interface Props {
  title: string
  question: string
}

defineProps<Props>()
</script>

<template>
  <section class="narrative-section">
    <div class="section-header">
      <h2 class="section-title">{{ title }}</h2>
      <p class="section-question">{{ question }}</p>
    </div>
    <div class="section-body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
@reference "@/styles/main.css";

.narrative-section {
  @apply flex flex-col gap-4;
}

.section-header {
  @apply bg-gray-50 py-3 border-b border-gray-200;
}

.section-title {
  @apply text-2xl font-bold text-gray-900;
}

.section-question {
  @apply text-xl text-gray-500 mt-0.5;
}

.section-body {
  @apply grid gap-4 md:gap-6;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .section-body {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
