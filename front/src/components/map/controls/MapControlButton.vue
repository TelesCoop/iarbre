<script lang="ts" setup>
import { computed } from "vue"

type ButtonSize = "sm" | "md"

interface Props {
  active?: boolean
  size?: ButtonSize
  ariaLabel?: string
  ariaPressed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  active: false,
  size: "sm",
  ariaLabel: undefined,
  ariaPressed: undefined
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const sizeClasses: Record<ButtonSize, string> = {
  sm: "map-control-btn-sm",
  md: "map-control-btn-md"
}

const buttonClasses = computed(() => [
  "map-control-btn",
  sizeClasses[props.size],
  props.active ? "map-control-btn-active" : ""
])

const handleClick = (event: MouseEvent) => {
  emit("click", event)
}
</script>

<template>
  <button
    :aria-label="ariaLabel"
    :aria-pressed="ariaPressed"
    :class="buttonClasses"
    type="button"
    @click="handleClick"
  >
    <slot />
  </button>
</template>
