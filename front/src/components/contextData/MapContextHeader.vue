<script lang="ts" setup>
interface MapContextHeaderProps {
  title: string
  description?: string
}

defineProps<MapContextHeaderProps>()
const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <header class="relative">
    <div>
      <p v-if="description" id="plantability-description" class="text-xs">
        <i aria-hidden="true" class="pi pi-info-circle mr-2"></i>
        {{ description }}
      </p>
    </div>
  </header>
</template>
