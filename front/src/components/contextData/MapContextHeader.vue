<script lang="ts" setup>
interface MapContextHeaderProps {
  title: string
  description?: string
}

defineProps<MapContextHeaderProps>()
const emit = defineEmits<{
  close: []
}>()
const handleClose = () => {
  emit("close")
}
</script>

<template>
  <header class="bg-primary-500 text-white relative">
    <div class="absolute right-0 mb-2 pr-4">
      <button
        class="h-8 w-8 p-2 md:p-4 mt-4 rounded-full hover:bg-white/20 focus:bg-white/20 transition-colors hover:text-white focus:text-white focus:outline-none focus:ring-2 focus:ring-white/50 flex items-center justify-center"
        data-cy="close-plantability-context-data"
        type="button"
        @click="handleClose"
      >
        <i aria-hidden="true" class="pi pi-times text-xl"></i>
      </button>
    </div>
    <div class="p-2 md:p-4">
      <h2 id="plantability-title" class="text-md mb-2 pr-8">{{ title }}</h2>

      <p v-if="description" id="plantability-description" class="text-sm opacity-90">
        <i aria-hidden="true" class="pi pi-info-circle mr-2"></i>
        {{ description }}
      </p>
    </div>
  </header>
</template>
