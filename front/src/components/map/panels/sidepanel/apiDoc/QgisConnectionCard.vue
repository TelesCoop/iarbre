<script lang="ts" setup>
import { copyToClipboard } from "@/utils/clipboard"

defineProps<{
  baseUrl: string
  steps: string[]
}>()
</script>

<template>
  <div class="border border-primary-300 rounded-lg overflow-hidden shadow-sm">
    <div class="flex items-center gap-2 px-3 py-2 bg-primary-500">
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="white"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M9 17H7A5 5 0 017 7h2M15 7h2a5 5 0 010 10h-2M8 12h8" />
      </svg>
      <span class="text-xs font-bold text-white tracking-wide">CONNEXION QGIS</span>
    </div>
    <div class="px-3 py-3 bg-primary-50 space-y-2.5">
      <ol class="text-xs text-primary-900 space-y-1 list-decimal list-inside">
        <li v-for="step in steps" :key="step">{{ step }}</li>
      </ol>
      <div
        class="flex items-center gap-2 bg-white border border-primary-200 rounded-md pl-2.5 pr-1.5 py-1.5"
      >
        <span class="font-mono text-xs text-primary-700 flex-1 truncate">{{ baseUrl }}</span>
        <button
          type="button"
          class="text-2xs font-semibold text-white bg-primary-500 hover:bg-primary-600 transition-colors rounded px-2 py-1 shrink-0"
          @click="copyToClipboard(baseUrl)"
        >
          Copier
        </button>
      </div>
    </div>
  </div>
</template>
