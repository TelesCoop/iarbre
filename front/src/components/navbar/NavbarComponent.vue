<script lang="ts" setup>
import { ref } from "vue"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import type { Feedback } from "@/types"
import Button from "primevue/button"
import { useToast } from "primevue"

const feedbackIsVisible = ref(false)
const toast = useToast()

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
    life: 5000
  })
  feedbackIsVisible.value = false
  return true
}
</script>

<template>
  <div class="header">
    <div class="header-logo">
      <a href="#">
        <img alt="Logo I-Arbre" class="h-10 w-auto" src="/images/logo-iarbre.png" />
      </a>
    </div>
    <nav class="header-nav">
      <ul class="nav-list">
        <li>
          <Button
            data-cy="open-feedback-button"
            severity="primary"
            type="button"
            @click="feedbackIsVisible = true"
            >✉️ Nous envoyer votre retour
          </Button>
        </li>
        <li>
          <a class="link" data-cy="open-savoir-href" href="https://iarbre.fr" target="_blank">
            ⓘ En savoir plus
          </a>
        </li>
      </ul>
    </nav>
  </div>
  <feedback-popin
    :model-value="feedbackIsVisible"
    @close="feedbackIsVisible = false"
    @submit-feedback="sendFeedbackToAPI"
  />
  <Toast />
</template>

<style scoped>
@reference "@/styles/main.css";
.header {
  @apply fixed top-0 w-full h-[var(--header-height)] z-10;
  @apply flex items-center justify-between;
  @apply overflow-hidden box-border;
}

.header-logo {
  @apply pl-4 md:pl-0;
}

.header-nav {
  @apply pr-4 md:pr-20;
}

.nav-list {
  @apply flex items-center gap-4 list-none;
}
</style>
