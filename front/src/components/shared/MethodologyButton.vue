<script lang="ts" setup>
import AppButton from "@/components/shared/AppButton.vue"
import IconInfo from "@/components/icons/IconInfo.vue"

const DOCUMENTATION_URL =
  "https://erasme.notion.site/Documentation-IA-rbre-33444e49a3ad80af8d9ef01b578e1192"

const openMethodology = () => {
  window.open(DOCUMENTATION_URL, "_blank", "noopener,noreferrer")
}
</script>

<template>
  <AppButton
    class="methodology-button"
    data-cy="methodology-button"
    size="sm"
    title="Documentation sur la méthodologie - nouvelle fenêtre"
    variant="gold"
    @click="openMethodology"
  >
    <template #icon-left>
      <IconInfo :size="14" aria-hidden="true" />
    </template>
    <span class="sm:hidden">Méthodologie</span>
    <span class="hidden sm:inline">Voir la méthodologie</span>
  </AppButton>
</template>

<style scoped>
@reference "@/styles/main.css";

.methodology-button {
  @apply px-2.5 py-1 text-xs gap-1 whitespace-nowrap;
}
</style>
