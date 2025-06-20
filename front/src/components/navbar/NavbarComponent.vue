<script lang="ts" setup>
import { ref } from "vue"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import type { Feedback } from "@/types/map"
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
  <nav class="header-nav ml-auto">
    <ul class="nav-list">
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
  @apply pl-4 md:pl-0;
}

.nav-list {
  @apply flex items-center list-none;
}
</style>
