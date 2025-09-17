<script lang="ts" setup>
interface MapContextHeaderProps {
  description?: string
}

defineProps<MapContextHeaderProps>()
</script>

<template>
  <header class="relative">
    <div>
      <p id="header-description" class="text-xs">
        <i aria-hidden="true" class="pi pi-info-circle mr-2"></i>
        {{ description }}
      </p>
    </div>
  </header>
</template>
