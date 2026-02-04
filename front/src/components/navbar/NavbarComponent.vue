<script lang="ts" setup>
import { ref } from "vue"
import { useApiPost } from "@/api"
import { useAppStore } from "@/stores/app"
import AppDrawer from "@/components/AppDrawer.vue"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import WelcomeMessage from "@/components/WelcomeMessage.vue"
import type { Feedback } from "@/types/map"
import AppButton from "@/components/shared/AppButton.vue"
import { useToast } from "@/composables/useToast"

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
        <AppButton
          data-cy="open-features-button"
          variant="text"
          size="sm"
          @click="welcomeIsVisible = true"
        >
          Tutoriel
        </AppButton>
      </li>
      <li>
        <AppButton
          data-cy="open-feedback-button"
          variant="text"
          size="sm"
          @click="feedbackIsVisible = true"
        >
          Envoyer votre avis
        </AppButton>
      </li>
    </ul>
  </nav>

  <!-- Mobile menu button -->
  <nav v-else class="block ml-auto">
    <AppButton
      variant="text"
      size="sm"
      data-cy="mobile-menu-button"
      @click="toggleMobileMenu"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </AppButton>
  </nav>

  <!-- Mobile menu -->
  <AppDrawer
    v-model:visible="mobileMenuVisible"
    position="right"
    :custom-styles="{ width: '16rem', maxWidth: '16rem' }"
    class="sm:hidden"
    data-cy="mobile-menu"
  >
    <div class="p-4">
      <ul class="space-y-4">
        <li>
          <AppButton
            data-cy="mobile-features-button"
            variant="text"
            size="sm"
            class="w-full justify-start"
            @click="
              () => {
                welcomeIsVisible = true
                closeMobileMenu()
              }
            "
          >
            Tutoriel
          </AppButton>
        </li>
        <li>
          <AppButton
            data-cy="mobile-feedback-button"
            variant="text"
            size="sm"
            class="w-full justify-start"
            @click="
              () => {
                feedbackIsVisible = true
                closeMobileMenu()
              }
            "
          >
            Envoyer votre avis
          </AppButton>
        </li>
      </ul>
    </div>
  </AppDrawer>

  <WelcomeMessage v-model="welcomeIsVisible" />

  <FeedbackPopin
    :model-value="feedbackIsVisible"
    @close="feedbackIsVisible = false"
    @submit-feedback="sendFeedbackToAPI"
  />
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
