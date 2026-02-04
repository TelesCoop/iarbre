<script lang="ts" setup>
import { computed } from "vue"

interface Props {
  modelValue: boolean
  labelId?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  labelId: undefined,
  disabled: false
})

const emit = defineEmits<{
  "update:modelValue": [value: boolean]
}>()

const isActive = computed(() => props.modelValue)

const toggleClasses = computed(() => [
  "toggle-switch",
  isActive.value ? "toggle-switch-active" : "",
  props.disabled ? "toggle-switch-disabled" : ""
])

const handleToggle = () => {
  if (!props.disabled) {
    emit("update:modelValue", !props.modelValue)
  }
}
</script>

<template>
  <button
    :aria-checked="isActive"
    :aria-labelledby="labelId"
    :class="toggleClasses"
    :disabled="disabled"
    role="switch"
    type="button"
    @click="handleToggle"
  >
    <span class="toggle-switch-thumb"></span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

.toggle-switch {
  @apply relative inline-flex items-center;
  @apply w-10 h-6 rounded-full;
  @apply bg-gray-200 border border-gray-300;
  @apply cursor-pointer transition-colors duration-200;
}

.toggle-switch:hover:not(:disabled) {
  @apply bg-gray-300;
}

.toggle-switch:focus-visible {
  @apply outline-none ring-2 ring-primary-300 ring-offset-2;
}

.toggle-switch-active {
  @apply bg-primary-500 border-primary-500;
}

.toggle-switch-active:hover:not(:disabled) {
  @apply bg-primary-600;
}

.toggle-switch-disabled {
  @apply opacity-50 cursor-not-allowed;
}

.toggle-switch-thumb {
  @apply absolute w-4 h-4 rounded-full;
  @apply bg-white shadow-sm;
  @apply transition-transform duration-200;
  left: 3px;
}

.toggle-switch-active .toggle-switch-thumb {
  transform: translateX(16px);
}
</style>
