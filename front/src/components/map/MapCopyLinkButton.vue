<script lang="ts" setup>
import { ref } from "vue"
import { copyToClipboard } from "@/utils/clipboard"
import IconCheck from "@/components/icons/IconCheck.vue"
import IconCopy from "@/components/icons/IconCopy.vue"

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
    aria-label="Copier le lien de cette vue"
    class="group flex items-center justify-center gap-1.5 py-1.5 px-2 lg:px-2.5 bg-white border border-gray-200 rounded-lg pointer-events-auto font-sans shrink-0 cursor-pointer transition-all"
    data-cy="copy-link-button"
    type="button"
    @click="handleCopyLink"
  >
    <IconCheck v-if="isCopied" class="text-primary-500 shrink-0" :size="14" />
    <IconCopy v-else class="text-primary-500 shrink-0" :size="14" />
    <span
      class="text-xs lg:text-sm font-medium whitespace-nowrap"
      :class="isCopied ? 'text-primary-600' : 'text-gray-500 group-hover:text-primary-600'"
      >{{ isCopied ? "Lien copié" : "Copier le lien de la vue" }}</span
    >
  </button>
</template>
