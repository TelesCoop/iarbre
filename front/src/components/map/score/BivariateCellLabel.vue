<script lang="ts" setup>
import { computed } from "vue"

interface BivariateCellLabelProps {
  plantability: number
  vulnerability: number
  color: string
  highlighted?: boolean
}

const props = defineProps<BivariateCellLabelProps>()

const isHighlighted = computed(() => {
  const highlighted = props.highlighted || false
  return highlighted
})
</script>

<template>
  <div
    class="relative"
    :class="[isHighlighted ? 'ring-2' : '']"
    :style="{ backgroundColor: props.color }"
    style="width: 15px; height: 15px"
  ></div>
</template>
