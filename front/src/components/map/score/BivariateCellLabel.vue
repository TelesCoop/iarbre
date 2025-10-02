<script lang="ts" setup>
import { computed } from "vue"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface BivariateCellLabelProps {
  plantability: number
  vulnerability: number
  color: string
  isSelected?: boolean
  clickable?: boolean
}

const props = defineProps<BivariateCellLabelProps>()

const emit = defineEmits<{
  click: [plantability: number, vulnerability: number]
}>()

const isSelected = computed(() => props.isSelected || false)
const isClickable = computed(() => props.clickable || false)

const handleClick = () => {
  if (isClickable.value) {
    emit("click", props.plantability, props.vulnerability)
  }
}
</script>

<template>
  <div
    class="relative"
    :class="[
      isClickable ? 'cursor-pointer hover:scale-110 transition-transform duration-200' : '',
      isSelected ? 'border-2 border-primary-900 rounded-sm' : ''
    ]"
    :style="{ backgroundColor: props.color }"
    :title="
      isClickable
        ? `Plantabilité: ${plantability}, Vulnérabilité: ${vulnerability} - Cliquez pour ${isSelected ? 'désactiver' : 'activer'} le filtre`
        : undefined
    "
    style="width: 15px; height: 15px"
    @click="handleClick"
  >
    <FilterIndicator :is-visible="isSelected" />
  </div>
</template>
