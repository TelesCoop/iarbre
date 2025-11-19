<script lang="ts" setup>
import Button from "primevue/button"
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-off-white px-4">
    <div class="flex flex-col items-center text-center max-w-md">
      <i class="pi pi-exclamation-circle text-6xl! mb-6 text-light-green"></i>

      <h1 class="text-6xl font-bold mb-4 text-brown font-accent">404</h1>
      <h2 class="text-2xl font-semibold mb-2 text-brown">Page non trouvée</h2>
      <p class="text-base mb-8 text-gray-600">
        La page que vous recherchez n'existe pas ou a été déplacée.
      </p>

      <router-link to="/">
        <Button label="Retour à l'accueil" severity="primary" size="large" />
      </router-link>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>
