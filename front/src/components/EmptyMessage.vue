<script lang="ts" setup>
interface EmptyStateProps {
  message: string
  icon?: string
}

withDefaults(defineProps<EmptyStateProps>(), {
  icon: "pi-info-circle"
})
</script>

<template>
  <div
    aria-live="polite"
    class="flex items-center justify-center h-full text-gray-500 text-md bg-gray-100 p-4 rounded-lg border border-dashed border-gray-100"
    role="status"
  >
    <i :class="`pi ${icon} mr-2`" aria-hidden="true"></i>
    {{ message }}
  </div>
</template>
