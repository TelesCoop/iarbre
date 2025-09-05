<script lang="ts" setup>
interface Props {
  isVisible: boolean
}

defineProps<Props>()

const transitionProps = {
  "enter-active-class": "transition-all duration-200 ease-out",
  "enter-from-class": "opacity-0 scale-0",
  "enter-to-class": "opacity-100 scale-100",
  "leave-active-class": "transition-all duration-150 ease-in",
  "leave-from-class": "opacity-100 scale-100",
  "leave-to-class": "opacity-0 scale-0"
}
</script>
<template>
  <Transition v-bind="transitionProps">
    <div
      v-if="isVisible"
      class="absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full border border-white flex items-center justify-center"
    >
      <span class="text-white text-xs font-bold">✓</span>
    </div>
  </Transition>
</template>
