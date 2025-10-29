<script lang="ts" setup>
interface MapContextHeaderProps {
  description?: string
  title?: string
}

defineProps<MapContextHeaderProps>()
</script>

<template>
  <header class="relative">
    <div>
      <p id="header-description" class="text-xs mb-2">
        <i aria-hidden="true" class="pi pi-info-circle mr-2"></i>
        {{ description }}
      </p>
      <a
        v-if="title !== 'ipave'"
        :href="`https://docs.iarbre.fr/methodology/${title}/`"
        target="_blank"
        class="text-sm text-center font-sans block hover:text-gray-500"
      >
        Voir la méthodologie ici
      </a>
    </div>
  </header>
</template>
