<script lang="ts" setup>
import { ref } from "vue"
import { useApiPost } from "@/api"
import { useAppStore } from "@/stores/app"
import AppDrawer from "@/components/AppDrawer.vue"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import WelcomeMessage from "@/components/WelcomeMessage.vue"
import type { Feedback } from "@/types/map"
import Button from "primevue/button"
import { useToast } from "primevue"

const appStore = useAppStore()
const feedbackIsVisible = ref(false)
const welcomeIsVisible = ref(false)
const mobileMenuVisible = ref(false)
const toast = useToast()

const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

const closeMobileMenu = () => {
  mobileMenuVisible.value = false
}

const sendFeedbackToAPI = async (data: Feedback) => {
  const { error } = await useApiPost<Feedback>("feedback/", data)
  if (error != null) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: "Erreur lors de l'envoi du retour. Veuillez réessayer plus tard."
    })
    return false
  }
  toast.add({
    severity: "success",
    summary: "Merci !",
    detail: "Votre retour a bien été envoyé",
    life: 5000,
    group: "br"
  })
  feedbackIsVisible.value = false
  return true
}
</script>

<template>
  <div class="header-logo">
    <a href="#">
      <img alt="Logo I-Arbre" class="h-8 sm:h-10 w-auto" src="/images/logo-iarbre.png" />
    </a>
  </div>
  <nav v-if="appStore.isDesktop" class="header-nav ml-auto block">
    <ul class="nav-list">
      <li>
        <Button
          data-cy="open-features-button"
          severity="primary"
          size="small"
          type="button"
          variant="text"
          @click="welcomeIsVisible = true"
          >Afficher les fonctionnalités
        </Button>
      </li>
      <li>
        <Button
          data-cy="open-feedback-button"
          severity="primary"
          size="small"
          type="button"
          variant="text"
          @click="feedbackIsVisible = true"
          >Envoyer votre avis
        </Button>
      </li>
    </ul>
  </nav>

  <!-- Mobile menu button -->
  <nav v-else class="block ml-auto">
    <Button
      icon="pi pi-bars"
      severity="primary"
      size="small"
      type="button"
      variant="text"
      data-cy="mobile-menu-button"
      @click="toggleMobileMenu"
    />
  </nav>

  <!-- Mobile menu -->
  <AppDrawer
    v-model:visible="mobileMenuVisible"
    position="right"
    :custom-styles="{ width: '16rem', maxWidth: '16rem' }"
    class="sm:hidden"
    data-cy="mobile-menu"
  >
    <template #header>
      <div class="flex justify-end">
        <Button
          icon="pi pi-times"
          severity="primary"
          size="small"
          type="button"
          variant="text"
          data-cy="mobile-menu-close"
          @click="closeMobileMenu"
        />
      </div>
    </template>

    <div class="p-4">
      <ul class="space-y-4">
        <li>
          <Button
            data-cy="mobile-features-button"
            severity="primary"
            size="small"
            type="button"
            variant="text"
            class="w-full justify-start"
            @click="
              () => {
                welcomeIsVisible = true
                closeMobileMenu()
              }
            "
            >Afficher les fonctionnalités
          </Button>
        </li>
        <li>
          <Button
            data-cy="open-feedback-button"
            severity="primary"
            size="small"
            type="button"
            variant="text"
            class="w-full justify-start"
            @click="
              () => {
                feedbackIsVisible = true
                closeMobileMenu()
              }
            "
            >Envoyer votre avis
          </Button>
        </li>
      </ul>
    </div>
  </AppDrawer>

  <welcome-message v-model="welcomeIsVisible" />

  <feedback-popin
    :model-value="feedbackIsVisible"
    @close="feedbackIsVisible = false"
    @submit-feedback="sendFeedbackToAPI"
  />
  <Toast group="tl" position="top-left" />
  <Toast group="tr" position="top-right" />
  <Toast group="bl" position="bottom-left" />
  <Toast group="br" position="bottom-right" />
</template>

<style scoped>
@reference "@/styles/main.css";
.header-logo {
  @apply pl-2 lg:pl-0;
}

.nav-list {
  @apply flex items-center list-none;
}
</style>
