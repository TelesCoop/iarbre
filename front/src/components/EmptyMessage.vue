<script lang="ts" setup>
interface EmptyStateProps {
  message: string
  icon?: string
}

const props = withDefaults(defineProps<EmptyStateProps>(), {
  icon: "pi-info-circle"
})
</script>

<template>
  <div
    class="flex items-center justify-center h-full text-gray-500 text-sm"
    role="status"
    aria-live="polite"
  >
    <i :class="`pi ${icon} mr-2`" aria-hidden="true"></i>
    {{ message }}
  </div>
</template>
