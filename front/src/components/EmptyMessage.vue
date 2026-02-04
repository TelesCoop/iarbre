<script lang="ts" setup>
import IconInfo from "@/components/icons/IconInfo.vue"

interface EmptyStateProps {
  message: string
}

defineProps<EmptyStateProps>()
</script>

<template>
  <div
    aria-live="polite"
    class="flex items-center justify-center h-full text-gray-500 text-base bg-gray-100 p-4 rounded-lg border border-dashed border-gray-100"
    role="status"
  >
    <IconInfo class="mr-2" :size="20" aria-hidden="true" />
    {{ message }}
  </div>
</template>
