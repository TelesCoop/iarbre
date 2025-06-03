<script lang="ts" setup>
const emit = defineEmits<{
  close: []
}>()

const handleClose = () => {
  emit("close")
}
</script>

<template>
  <header class="bg-primary-500 text-white p-4 relative">
    <div class="flex justify-end mb-2">
      <button
        type="button"
        class="h-8 w-8 p-1 rounded-full hover:bg-white/20 focus:bg-white/20 transition-colors hover:text-white focus:text-white focus:outline-none focus:ring-2 focus:ring-white/50"
        data-cy="close-plantability-card"
        aria-label="Fermer la carte de plantabilité"
        @click="handleClose"
      >
        <i class="pi pi-times text-xl" aria-hidden="true"></i>
      </button>
    </div>

    <h2 id="plantability-title" class="text-xl font-semibold mb-2 pr-8">Score de plantabilité</h2>

    <p id="plantability-description" class="text-sm opacity-90">
      <i class="pi pi-info-circle mr-2" aria-hidden="true"></i>
      Calcul basé sur la pondération de 30 paramètres
    </p>
  </header>
</template>
