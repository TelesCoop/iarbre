<script lang="ts" setup>
import { computed } from "vue"
import { SelectionMode } from "@/utils/enum"

interface Props {
  mode: SelectionMode
  icon: string
  label: string
  active: boolean
  disabled?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [mode: SelectionMode]
}>()

const buttonClasses = computed(() => [
  "map-control-btn map-control-btn-sm",
  props.active ? "map-control-btn-active" : "",
  props.disabled ? "map-control-btn-disabled" : ""
])

const iconSrc = computed(() => `/icons/${props.icon}${props.active ? "-white" : ""}.svg`)

const handleClick = () => {
  if (props.disabled) return
  emit("select", props.mode)
}
</script>

<template>
  <button
    v-tooltip.left="label"
    :aria-label="label"
    :aria-pressed="active"
    :class="buttonClasses"
    :disabled="disabled"
    type="button"
    @click="handleClick"
  >
    <img :src="iconSrc" alt="" aria-hidden="true" class="w-6 h-6" />
  </button>
</template>
