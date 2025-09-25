<script lang="ts" setup>
import { ref, onMounted } from "vue"
import { LocalStorageHandler } from "@/utils/LocalStorageHandler"

const showWelcome = ref(false)

onMounted(() => {
  const hasVisited = LocalStorageHandler.getItem("hasVisitedBefore")
  if (!hasVisited) {
    showWelcome.value = true
  }
})

const closeWelcome = () => {
  showWelcome.value = false
  LocalStorageHandler.setItem("hasVisitedBefore", true)
}
</script>

<template>
  <Dialog
    v-model:visible="showWelcome"
    :draggable="false"
    :style="{ width: '28rem' }"
    header="Bienvenue !"
    modal
    :closable="false"
  >
    <div class="flex flex-col gap-4 bg-white">
      <p class="mb-2">Découvrez les fonctionnalités :</p>

      <div class="space-y-4">
        <div class="welcome-functionnality">
          <span class="text-2xl">🗺️</span>
          <div>
            <h4 class="font-medium">Cliquez sur la carte</h4>
            <p class="text-sm">pour obtenir des informations détaillées sur une zone.</p>
          </div>
        </div>

        <div class="welcome-functionnality">
          <svg class="w-14 h-6" viewBox="0 0 240 50">
            <path fill="#C4C4C4" d="M0 0h40v50H0z" />
            <path fill="#BF5A16" d="M40 0h40v50H40z" />
            <path fill="#DDAD14" d="M80 0h40v50H80z" />
            <path fill="#A6CC4A" d="M120 0h40v50h-40z" />
            <path fill="#55B250" d="M160 0h40v50h-40z" />
            <path fill="#025400" d="M200 0h40v50h-40z" />
          </svg>
          <div>
            <h4 class="font-medium">Cliquez sur la légende</h4>
            <p class="text-sm">pour filtrer et masquer certaines zones selon vos préférences.</p>
          </div>
        </div>

        <div class="welcome-functionnality">
          <span class="text-2xl">🔍</span>
          <div>
            <h4 class="font-medium">Changez de calque</h4>
            <p class="text-sm">
              en utilisant les menus à gauche, vous pouvez aussi changer le fond de carte.
            </p>
          </div>
        </div>

        <div class="welcome-functionnality">
          <span class="text-2xl">💬</span>
          <div>
            <h4 class="font-medium">Donnez votre avis</h4>
            <p class="text-sm">
              en cliquant sur "Envoyer votre avis" pour partager vos commentaires.
            </p>
          </div>
        </div>

        <div class="welcome-functionnality">
          <span class="text-2xl">✉️</span>
          <div>
            <h4 class="font-medium">En savoir plus</h4>
            <p class="text-sm">
              en vous abonnant à la
              <a href="https://iarbre.fr/#newsletter" class="text-primary-900 font-medium underline"
                >newsletter</a
              >.
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Compris !" class="w-full" @click="closeWelcome" />
    </template>
  </Dialog>
</template>
