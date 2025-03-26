<script setup lang="ts">
import { ref } from "vue"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import type { Feedback } from "@/types"

const feedbackIsVisible = ref(false)
const feedbackMessage = ref("")

const sendFeedbackToAPI = async (data: Feedback) => {
  if (!data.feedback) {
    feedbackMessage.value = "Veuillez remplir un avis."
    return
  }

  const { error } = await useApiPost<Feedback>("feedback/", data)
  if (error != null) {
    feedbackMessage.value =
      "Erreur lors de l'envoi de votre feedback, merci de réessayer plus tard."
    return false
  }
  feedbackMessage.value = "Merci pour votre retour !"
  setTimeout(() => {
    feedbackIsVisible.value = false
    feedbackMessage.value = ""
  }, 1500)
  return true
}
</script>

<template>
  <div class="header">
    <div class="header-logo">
      <a href="/">
        <img class="h-10 w-auto" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </a>
    </div>
    <nav class="header-nav">
      <ul class="nav-list">
        <li>
          <button
            class="button"
            data-cy="open-feedback-button"
            @click.prevent="feedbackIsVisible = true"
          >
            ✉️ Nous envoyer votre retour
          </button>
        </li>
        <li>
          <a href="https://iarbre.fr" class="link" data-cy="open-savoir-href"> ⓘ En savoir plus </a>
        </li>
      </ul>
    </nav>
  </div>
  <feedback-popin
    v-if="feedbackIsVisible"
    :message="feedbackMessage"
    @submit-feedback="sendFeedbackToAPI"
    @close="feedbackIsVisible = false"
  />
</template>
