<script lang="ts" setup>
const emit = defineEmits<{
  close: []
}>()

const handleClose = () => {
  emit("close")
}
</script>

<template>
  <header class="bg-primary-500 text-white relative">
    <div class="absolute right-0 mb-2 pr-4">
      <button
        type="button"
        class="h-4 w-4 md:h-8 md:w-8 p-2 md:p-4 rounded-full hover:bg-white/20 focus:bg-white/20 transition-colors hover:text-white focus:text-white focus:outline-none focus:ring-2 focus:ring-white/50"
        data-cy="close-plantability-context-data"
        aria-label="Fermer la carte de plantabilité"
        @click="handleClose"
      >
        <i class="pi pi-times text-xl" aria-hidden="true"></i>
      </button>
    </div>
    <div class="p-2 md:p-4">
      <h2 id="plantability-title" class="text-xl font-semibold mb-2 pr-8">Score de plantabilité</h2>

      <p id="plantability-description" class="text-sm opacity-90">
        <i class="pi pi-info-circle mr-2" aria-hidden="true"></i>
        Calcul basé sur la pondération de +37 paramètres
      </p>
    </div>
  </header>
</template>
