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
    class="copy-link-button"
    data-cy="copy-link-button"
    type="button"
    @click="handleCopyLink"
  >
    <svg
      v-if="isCopied"
      class="copy-link-icon copied-icon"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      viewBox="0 0 24 24"
    >
      <path d="M20 6L9 17l-5-5" />
    </svg>
    <svg
      v-else
      class="copy-link-icon"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      viewBox="0 0 24 24"
    >
      <path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3" />
      <line x1="8" x2="16" y1="12" y2="12" />
    </svg>
    <span class="copy-link-text">{{ isCopied ? "Lien copié" : "Copier le lien de la vue" }}</span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

.copy-link-button {
  @apply inline-flex items-center pointer-events-auto w-fit;
  @apply gap-1.5 py-1.5 px-2;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply font-sans text-2xs font-medium text-gray-500;
  @apply cursor-pointer transition-all;
}

@media (min-width: 1024px) {
  .copy-link-button {
    @apply text-xs py-1.5 px-2.5;
  }
}

.copy-link-button:hover {
  @apply border-primary-500 bg-gray-50;
}

.copy-link-button:active {
  @apply scale-[0.98];
}

.copy-link-button.copied {
  @apply border-primary-500 bg-primary-50;
}

.copied-icon {
  @apply text-primary-500;
}

.copy-link-icon {
  @apply text-gray-400 shrink-0 w-2.5 h-2.5;
}

.copy-link-button:hover .copy-link-icon {
  @apply text-primary-500;
}

@media (min-width: 1024px) {
  .copy-link-icon {
    @apply w-3 h-3;
  }
}

.copy-link-text {
  @apply whitespace-nowrap;
}
</style>
