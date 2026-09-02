<script lang="ts" setup>
interface Props {
  title?: string
  subtitle?: string
}

withDefaults(defineProps<Props>(), {
  title: undefined,
  subtitle: undefined
})
</script>

<template>
  <div class="widget-card">
    <div class="widget-header">
      <h3 class="widget-title">
        <slot name="title">{{ title }}</slot>
      </h3>
      <p v-if="subtitle" class="widget-subtitle">{{ subtitle }}</p>
    </div>
    <div class="widget-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-card {
  @apply bg-white rounded-xl border border-gray-200;
  @apply p-4 md:p-6;
  @apply flex flex-col;
  @apply transition-shadow duration-200;
  min-height: 280px;
}

.widget-card:hover {
  @apply shadow-md;
}

.widget-header {
  @apply mb-4;
}

.widget-title {
  @apply text-sm md:text-base font-semibold text-gray-900;
}

.widget-title :deep(a) {
  @apply text-primary-500 underline underline-offset-2;
}

.widget-title :deep(a:hover) {
  @apply text-primary-800;
}

.widget-subtitle {
  @apply text-sm text-gray-800 mt-0.5;
}

.widget-content {
  @apply flex-1 flex flex-col items-center justify-center;
}

@media print {
  .widget-card {
    @apply border-0 p-0 shadow-none;
    min-height: 0;
    break-inside: avoid;
  }
}
</style>
