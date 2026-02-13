<script lang="ts" setup>
import AppButton from "@/components/shared/AppButton.vue"
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-off-white px-4">
    <div class="flex flex-col items-center text-center max-w-md">
      <svg
        class="w-16 h-16 mb-6 text-light-green"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>

      <h1 class="text-6xl font-bold mb-4 text-brown font-accent">404</h1>
      <h2 class="text-2xl font-semibold mb-2 text-brown">Page non trouvée</h2>
      <p class="text-base mb-8 text-gray-600">
        La page que vous recherchez n'existe pas ou a été déplacée.
      </p>

      <router-link to="/">
        <AppButton variant="primary" size="lg">Retour à l'accueil</AppButton>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>
