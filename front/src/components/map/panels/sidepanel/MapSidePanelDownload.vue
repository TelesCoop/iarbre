<script lang="ts" setup>
import { ref } from "vue"
import ApiDocDialog from "@/components/map/panels/sidepanel/ApiDocDialog.vue"

const apiDocVisible = ref(false)
</script>

<template>
  <div class="flex w-full font-sans text-white text-base text-center px-3 pt-2">
    <div class="w-full flex items-center justify-center gap-4">
      <span class="text-base font-serif font-bold">🌱 Intéressé·e par la plateforme ?</span>
      <div class="flex flex-col gap-4">
        <button
          class="cursor-pointer bg-white font-sans flex items-center px-4 py-2 rounded-3xl text-sm text-primary-500"
          data-cy="api-doc"
          @click="apiDocVisible = true"
        >
          Obtenir les données
          <svg
            class="ml-2"
            fill="none"
            height="16"
            viewBox="0 0 16 16"
            width="16"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11.5 5.5L14 8M14 8L11.5 10.5M14 8H2"
              stroke="#426A45"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
        <button
          class="cursor-pointer bg-white font-sans flex items-center px-2 py-2 rounded-3xl text-sm text-primary-500"
          data-cy="api-doc"
          @click="apiDocVisible = true"
        >
          Voir la méthodologie
          <svg
            class="ml-2"
            fill="none"
            height="16"
            viewBox="0 0 16 16"
            width="16"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M11.5 5.5L14 8M14 8L11.5 10.5M14 8H2"
              stroke="#426A45"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
  <ApiDocDialog v-model:visible="apiDocVisible" />
</template>
