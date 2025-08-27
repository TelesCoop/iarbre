<script lang="ts" setup>
interface MapContextHeaderProps {
  title: string
  description?: string
  hideCloseButton?: boolean
}

defineProps<MapContextHeaderProps>()
const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <header class="relative">
    <div>
      <h2 id="plantability-title" class="text-md mb-1 text-center">{{ title }}</h2>

      <p v-if="description" id="plantability-description" class="text-xs">
        <i aria-hidden="true" class="pi pi-info-circle mr-2"></i>
        {{ description }}
      </p>
    </div>
  </header>
</template>
