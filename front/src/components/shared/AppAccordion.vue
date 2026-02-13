<script lang="ts" setup>
import { ref, provide } from "vue"

interface AccordionProps {
  multiple?: boolean
}

const props = withDefaults(defineProps<AccordionProps>(), {
  multiple: false
})

const activeItems = ref<string[]>([])

const toggleItem = (value: string) => {
  const index = activeItems.value.indexOf(value)
  if (index === -1) {
    if (props.multiple) {
      activeItems.value.push(value)
    } else {
      activeItems.value = [value]
    }
  } else {
    activeItems.value.splice(index, 1)
  }
}

const isActive = (value: string) => activeItems.value.includes(value)

provide("accordion", {
  toggleItem,
  isActive
})
</script>

<template>
  <div class="app-accordion" role="tablist">
    <slot />
  </div>
</template>

<style scoped>
.app-accordion {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}
</style>
