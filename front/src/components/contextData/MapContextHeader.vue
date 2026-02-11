<script lang="ts" setup>
import IconInfo from "@/components/icons/IconInfo.vue"

interface MapContextHeaderProps {
  description?: string
  title?: string
}

defineProps<MapContextHeaderProps>()
</script>

<template>
  <header class="relative">
    <div>
      <p id="header-description" class="text-xs mb-2 flex items-start">
        <IconInfo class="mr-2 flex-shrink-0 mt-0.5" :size="14" aria-hidden="true" />
        {{ description }}
      </p>
      <a
        :href="`https://docs.iarbre.fr/methodology/${title}/`"
        target="_blank"
        class="text-sm text-center font-sans block hover:text-gray-500"
      >
        Voir la méthodologie ici
      </a>
    </div>
  </header>
</template>
