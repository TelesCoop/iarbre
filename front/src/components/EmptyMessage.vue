<script lang="ts" setup>
import IconInfo from "@/components/icons/IconInfo.vue"

interface EmptyStateProps {
  message: string
}

defineProps<EmptyStateProps>()
</script>

<template>
  <div aria-live="polite" class="empty-message" role="status">
    <span class="empty-message-icon">
      <IconInfo :size="20" aria-hidden="true" />
    </span>
    <p class="empty-message-text">{{ message }}</p>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.empty-message {
  @apply flex flex-col items-center justify-center gap-3 h-full;
  @apply px-6 py-8 text-center;
  @apply rounded-xl border border-dashed border-gray-200 bg-gray-50;
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='18'%20height='18'%3E%3Ccircle%20cx='2'%20cy='2'%20r='1.8'%20fill='%23426a45'%20fill-opacity='0.12'/%3E%3C/svg%3E");
  background-position: center;
}

.empty-message-icon {
  @apply flex items-center justify-center shrink-0;
  @apply w-11 h-11 rounded-full;
  @apply bg-primary-50 text-primary-500;
}

.empty-message-text {
  @apply max-w-56 text-sm font-medium leading-snug text-gray-500;
}
</style>
