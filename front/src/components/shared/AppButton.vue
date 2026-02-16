<script lang="ts" setup>
import { computed } from "vue"

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "text"
type ButtonSize = "sm" | "md" | "lg"

type ButtonType = "button" | "submit" | "reset"

interface ButtonProps {
  variant?: ButtonVariant
  size?: ButtonSize
  type?: ButtonType
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  rounded?: boolean
  iconOnly?: boolean
}

const props = withDefaults(defineProps<ButtonProps>(), {
  variant: "primary",
  size: "md",
  type: "button",
  disabled: false,
  loading: false,
  fullWidth: false,
  rounded: false,
  iconOnly: false
})

const emit = defineEmits<{
  (e: "click", event: MouseEvent): void
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit("click", event)
  }
}

const baseClasses = computed(() => {
  return [
    "inline-flex items-center justify-center",
    "font-sans font-medium",
    "transition-all duration-200",
    "cursor-pointer",
    "border",
    props.fullWidth ? "w-full" : "",
    props.rounded ? "rounded-full" : "rounded-lg",
    props.disabled || props.loading ? "opacity-50 cursor-not-allowed" : ""
  ]
    .filter(Boolean)
    .join(" ")
})

const sizeClasses = computed(() => {
  if (props.iconOnly) {
    switch (props.size) {
      case "sm":
        return "w-8 h-8 text-sm"
      case "lg":
        return "w-12 h-12 text-lg"
      default:
        return "w-10 h-10 text-base"
    }
  }

  switch (props.size) {
    case "sm":
      return "px-3 py-1.5 text-sm gap-1.5"
    case "lg":
      return "px-6 py-3 text-base gap-2"
    default:
      return "px-4 py-2 text-sm gap-2"
  }
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case "primary":
      return "bg-primary-500 text-white border-primary-500 hover:bg-primary-600 hover:border-primary-600 focus:ring-2 focus:ring-primary-200"
    case "secondary":
      return "bg-white text-gray-900 border-gray-200 hover:bg-primary-500 hover:text-white hover:border-primary-500 focus:ring-2 focus:ring-gray-200"
    case "outline":
      return "bg-transparent text-primary-500 border-primary-500 hover:bg-primary-50 focus:ring-2 focus:ring-primary-200"
    case "ghost":
      return "bg-transparent text-gray-700 border-transparent hover:bg-gray-100 focus:ring-2 focus:ring-gray-200"
    case "text":
      return "bg-transparent text-primary-500 border-transparent hover:text-primary-600 hover:underline p-0"
    default:
      return ""
  }
})

const buttonClasses = computed(() => {
  return [baseClasses.value, sizeClasses.value, variantClasses.value].join(" ")
})
</script>

<template>
  <button :class="buttonClasses" :disabled="disabled || loading" :type="type" @click="handleClick">
    <span v-if="loading" class="animate-spin">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path
          class="opacity-75"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          fill="currentColor"
        />
      </svg>
    </span>
    <slot v-else name="icon-left" />
    <span v-if="!iconOnly">
      <slot />
    </span>
    <slot v-else />
    <slot name="icon-right" />
  </button>
</template>
