<script lang="ts" setup>
import { computed } from "vue"
import type { ContextDataFactor, ContextDataColorScheme } from "@/types/contextData"

interface ContextDataItemProps {
  item: ContextDataFactor
  colorScheme?: ContextDataColorScheme
}

const props = withDefaults(defineProps<ContextDataItemProps>(), {
  colorScheme: "plantability"
})

const iconClasses = computed(() => {
  const base =
    "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-colors"

  if (props.colorScheme === "plantability" && props.item.impact) {
    switch (props.item.impact) {
      case "negative":
        return `${base} bg-orange-100 text-orange-700 text-lg`
      case "positive":
        return `${base} bg-green-100 text-green-700 text-lg`
      default:
        return `${base} bg-gray-200 text-gray-700 text-lg`
    }
  } else if (props.colorScheme === "climate") {
    return `${base} bg-primary-100 text-primary-700 text-sm font-bold`
  }

  return `${base} bg-gray-200 text-gray-700 text-lg`
})

const valueClasses = computed(() => {
  const base = "text-sm font-bold transition-colors"

  if (props.colorScheme === "plantability" && props.item.impact) {
    switch (props.item.impact) {
      case "negative":
        return `${base} text-orange-600`
      case "positive":
        return `${base} text-green-600`
      default:
        return `${base} text-gray-700`
    }
  } else if (props.colorScheme === "climate") {
    return `${base} text-primary-600`
  }

  return `${base} text-gray-700`
})

const containerClasses = computed(() => {
  return "flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 focus-within:bg-gray-100 transition-colors"
})
</script>

<template>
  <div role="listitem" :class="containerClasses" :data-cy="`factor-${item.key}`">
    <div
      v-if="item.icon"
      :class="iconClasses"
      :aria-label="`Icône pour ${item.label}`"
      data-cy="factor-icon"
    >
      {{ item.icon }}
    </div>

    <div class="flex-1 min-w-0" :class="{ 'ml-0': !item.icon }">
      <h4 class="text-sm font-medium text-gray-900 mb-1 truncate">
        {{ item.label }}
      </h4>
      <p v-if="item.description" class="text-xs text-gray-500 mb-1">
        {{ item.description }}
      </p>
      <p :class="valueClasses">
        {{ item.value }}
        <span v-if="item.unit" class="text-xs text-gray-500 font-normal ml-1">{{ item.unit }}</span>
      </p>
    </div>
  </div>
</template>
