<script lang="ts" setup>
import { computed } from "vue"
import { SelectionMode } from "@/utils/enum"

interface Props {
  mode: SelectionMode
  icon: string
  label: string
  active: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [mode: SelectionMode]
}>()

const buttonClasses = computed(() => [
  "map-control-btn map-control-btn-sm",
  props.active ? "map-control-btn-active" : ""
])

const iconSrc = computed(() => `/icons/${props.icon}${props.active ? "-white" : ""}.svg`)

const handleClick = () => {
  emit("select", props.mode)
}
</script>

<template>
  <button
    v-tooltip.left="label"
    :aria-label="label"
    :aria-pressed="active"
    :class="buttonClasses"
    type="button"
    @click="handleClick"
  >
    <img :src="iconSrc" alt="" aria-hidden="true" class="w-6 h-6" />
  </button>
</template>
