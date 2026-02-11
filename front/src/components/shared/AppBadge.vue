<script lang="ts" setup>
import { computed } from "vue"

type BadgeVariant = "primary" | "secondary" | "success" | "warning" | "danger" | "info"
type BadgeSize = "sm" | "md"

interface Props {
  variant?: BadgeVariant
  size?: BadgeSize
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "sm"
})

const variantClasses: Record<BadgeVariant, string> = {
  primary: "bg-primary-100 text-primary-700 border-primary-200",
  secondary: "bg-gray-100 text-gray-700 border-gray-200",
  success: "bg-green-100 text-green-700 border-green-200",
  warning: "bg-yellow-100 text-yellow-700 border-yellow-200",
  danger: "bg-red-100 text-red-700 border-red-200",
  info: "bg-blue-100 text-blue-700 border-blue-200"
}

const sizeClasses: Record<BadgeSize, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm"
}

const badgeClasses = computed(() => [
  "inline-flex items-center font-medium rounded-full border",
  variantClasses[props.variant],
  sizeClasses[props.size]
])
</script>

<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>
