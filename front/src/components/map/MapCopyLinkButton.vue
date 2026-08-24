<script lang="ts" setup>
import { ref } from "vue"
import { copyToClipboard } from "@/utils/clipboard"

const isCopied = ref(false)

const handleCopyLink = async () => {
  await copyToClipboard(window.location.href)
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}
</script>

<template>
  <button
    :class="{ copied: isCopied }"
    aria-label="Copier le lien de cette vue"
    class="copy-link"
    data-cy="copy-link-button"
    type="button"
    @click="handleCopyLink"
  >
    <svg
      v-if="isCopied"
      class="copy-link__icon"
      fill="none"
      stroke="currentColor"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2.5"
      viewBox="0 0 24 24"
    >
      <path d="M20 6L9 17l-5-5" />
    </svg>
    <svg
      v-else
      class="copy-link__icon"
      fill="none"
      stroke="currentColor"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      viewBox="0 0 24 24"
    >
      <path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3" />
      <line x1="8" x2="16" y1="12" y2="12" />
    </svg>
    <span class="copy-link__label">{{ isCopied ? "Lien copié" : "Copier le lien de la vue" }}</span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

/* Rendered as a footer row inside the legend panel, matching the divider
   treatment of the sibling .legend-attribution / .filters-status footers
   (border-gray-100). */
.copy-link {
  @apply flex items-center justify-center gap-2 w-full pt-1;
  @apply border-t border-gray-100;
  @apply cursor-pointer transition-colors duration-200;
}

.copy-link__icon {
  @apply text-primary-500 shrink-0 w-3.5 h-3.5;
}

.copy-link__label {
  @apply text-xs font-normal text-gray-700 whitespace-nowrap;
}

.copy-link:hover .copy-link__label,
.copy-link.copied .copy-link__label {
  @apply text-primary-600;
}
</style>
