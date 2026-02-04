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
          <span class="p-select-option-label">{{ option[optionLabel as keyof SelectOption] }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.app-select {
  position: relative;
  width: 100%;
}

.app-select.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.625rem 1rem;
  background: white;
  border: 1px solid #bcbcbc;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.875rem;
  font-family: inherit;
  color: #426a45;
  transition: all 0.2s;
}

.select-trigger:hover {
  border-color: #426a45;
}

.select-trigger.open {
  border-color: #426a45;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.select-value {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-value.placeholder {
  color: #9ca3af;
}

.select-icon {
  flex-shrink: 0;
  color: #426a45;
  margin-left: 0.5rem;
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #426a45;
  border-top: none;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.select-option {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.625rem 1rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-family: inherit;
  color: #374151;
  text-align: left;
  transition: background-color 0.15s;
}

.select-option:hover {
  background-color: #c7dbc0;
}

.select-option.selected {
  background-color: #edf5e9;
  color: #426a45;
  font-weight: 500;
}

.select-option:last-child {
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}

.select-dropdown-enter-active,
.select-dropdown-leave-active {
  transition: all 0.15s ease;
}

.select-dropdown-enter-from,
.select-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
