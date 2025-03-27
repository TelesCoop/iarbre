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
  console.log(error, data)
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
            ✉️ Nous envoyer votre retour {{ feedbackIsVisible }}
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

<style scoped>
@reference "../styles/main.css";
.header {
  @apply fixed top-0 w-full bg-off-white h-[var(--header-height)] z-10 flex items-center justify-between overflow-hidden box-border;
}

.header-logo {
  @apply pl-4 md:pl-0;
}

.header-nav {
  @apply pr-4 md:pr-20;
}

.nav-list {
  @apply flex gap-4 list-none;
}

.link {
  @apply font-mono text-brown text-base no-underline transition duration-300 hover:text-light-green;
}
</style>
