<script lang="ts" setup>
import { ref } from "vue"
import { copyToClipboard } from "@/utils/clipboard"
import AccordionSection from "./AccordionSection.vue"
import type { RequestParam } from "./types"

defineProps<{
  urlLabel: string
  url: string
  params: RequestParam[]
}>()

const open = ref(false)
</script>

<template>
  <AccordionSection :open="open" body-class="p-2.5 space-y-3" @toggle="open = !open">
    <template #header>
      <span class="text-2xs font-bold text-gray-500 tracking-wider"
        >CONSTRUIRE LA REQUÊTE MANUELLEMENT</span
      >
    </template>

    <div class="bg-gray-50 border border-gray-200 rounded-md overflow-hidden">
      <div class="flex items-center justify-between px-2.5 py-2 border-b border-gray-100">
        <span class="text-xs text-gray-400">{{ urlLabel }}</span>
        <button
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition-colors"
          @click="copyToClipboard(url)"
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
          </svg>
          Copier
        </button>
      </div>
      <button
        type="button"
        class="url-display block w-full text-left px-2.5 py-2 bg-white font-mono text-xs text-primary-500 hover:text-primary-700 cursor-pointer"
        @click="copyToClipboard(url)"
      >
        {{ url }}
      </button>
    </div>

    <div class="border border-gray-200 rounded-md overflow-hidden">
      <div
        class="grid grid-cols-[1fr_1fr_2fr] text-2xs font-bold text-gray-400 tracking-wider border-b border-gray-200 bg-gray-50 px-2.5 py-2"
      >
        <span>PARAMÈTRE</span>
        <span>VALEUR</span>
        <span>DESCRIPTION</span>
      </div>
      <div
        v-for="(param, i) in params"
        :key="param.key"
        class="grid grid-cols-[1fr_1fr_2fr] px-2.5 py-1.5 text-xs border-b border-gray-100 last:border-b-0"
        :class="i % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
      >
        <span class="font-mono text-primary-800">{{ param.key }}</span>
        <span class="font-mono text-scale-3">{{ param.value }}</span>
        <div class="flex items-center gap-2">
          <span class="text-gray-600">{{ param.desc }}</span>
          <span
            v-if="param.fixed"
            class="text-2xs text-gray-400 border border-gray-200 rounded px-1 shrink-0"
            >fixe</span
          >
        </div>
      </div>
    </div>
  </AccordionSection>
</template>

<style scoped>
.url-display {
  word-break: break-all;
  overflow-wrap: anywhere;
}
</style>
