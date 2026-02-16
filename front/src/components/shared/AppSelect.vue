<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import IconChevron from "@/components/icons/IconChevron.vue"

interface SelectOption {
  label: string
  value: string | number
}

interface Props {
  modelValue: string | number | null
  options: SelectOption[]
  optionLabel?: string
  optionValue?: string
  placeholder?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  optionLabel: "label",
  optionValue: "value",
  placeholder: "Sélectionner...",
  disabled: false
})

const emit = defineEmits<{
  (e: "update:modelValue", value: string | number): void
}>()

const isOpen = ref(false)
const selectRef = ref<HTMLElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find(
    (opt) => opt[props.optionValue as keyof SelectOption] === props.modelValue
  )
})

const displayValue = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value[props.optionLabel as keyof SelectOption]
  }
  return props.placeholder
})

const toggle = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

const selectOption = (option: SelectOption) => {
  emit("update:modelValue", option[props.optionValue as keyof SelectOption] as string | number)
  isOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape") {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside)
  document.addEventListener("keydown", handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside)
  document.removeEventListener("keydown", handleKeydown)
})
</script>

<template>
  <div ref="selectRef" class="app-select" :class="{ disabled }">
    <button
      type="button"
      class="select-trigger"
      :class="{ open: isOpen }"
      :disabled="disabled"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span class="select-value" :class="{ placeholder: !selectedOption }">
        {{ displayValue }}
      </span>
      <IconChevron :direction="isOpen ? 'up' : 'down'" :size="16" class="select-icon" />
    </button>

    <Transition name="select-dropdown">
      <div v-if="isOpen" class="select-dropdown" role="listbox">
        <button
          v-for="option in options"
          :key="String(option[optionValue as keyof SelectOption])"
          type="button"
          class="select-option"
          :class="{ selected: option[optionValue as keyof SelectOption] === modelValue }"
          role="option"
          :aria-selected="option[optionValue as keyof SelectOption] === modelValue"
          @click="selectOption(option)"
        >
          <span class="select-option-label">{{ option[optionLabel as keyof SelectOption] }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.app-select {
  position: relative;
  width: 100%;
}

.app-select.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.select-trigger {
  @apply flex items-center justify-between w-full;
  @apply py-1.5 px-3;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply cursor-pointer text-xs font-sans text-gray-700;
  @apply transition-all;
}

@media (min-width: 1024px) {
  .select-trigger {
    @apply py-2 px-4 text-sm;
  }
}

.select-trigger:hover {
  @apply border-primary-500;
}

.select-trigger.open {
  @apply border-primary-500;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.select-value {
  @apply flex-1 text-left truncate;
}

.select-value.placeholder {
  @apply text-gray-400;
}

.select-icon {
  @apply shrink-0 text-primary-500 ml-2;
}

.select-dropdown {
  @apply absolute top-full left-0 right-0;
  @apply bg-white border border-primary-500 border-t-0;
  @apply z-[1000] max-h-80 overflow-y-auto rounded-b-lg;
}

.select-option {
  @apply flex items-center w-full;
  @apply py-1.5 px-3;
  @apply bg-transparent border-none cursor-pointer;
  @apply text-xs font-sans text-gray-700 text-left;
  @apply transition-colors;
}

@media (min-width: 1024px) {
  .select-option {
    @apply py-2 px-4 text-sm;
  }
}

.select-option:hover {
  @apply bg-primary-200;
}

.select-option.selected {
  @apply bg-primary-100 text-primary-500 font-medium;
}

.select-option:last-child {
  @apply rounded-b-lg;
}

.select-dropdown-enter-active,
.select-dropdown-leave-active {
  @apply transition-all duration-150;
}

.select-dropdown-enter-from,
.select-dropdown-leave-to {
  @apply opacity-0 -translate-y-2;
}
</style>
