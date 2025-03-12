<script setup lang="ts">
import { ref } from "vue"
import { FULL_BASE_API_URL } from "@/utils/constants"
import FeedbackPopin from "@/components/FeedbackPopin.vue"

const isVisible = ref(false)

const sendFeedbackToAPI = async (data: { email: string; feedback: string }) => {
  try {
    const response = await fetch(`${FULL_BASE_API_URL}/feedback/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback: data.feedback, email: data.email })
    })
    if (!response.ok) {
      throw new Error("Erreur lors de l'envoi du feedback")
    }
    isVisible.value = false
  } catch (error) {
    console.error("Erreur lors de l'envoi du feedback:", error)
  }
}
</script>

<template>
  <div class="my-header">
    <div class="my-header-logo">
      <a href="/">
        <img class="h-10 w-auto" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </a>
    </div>
    <nav class="my-header-nav">
      <ul class="my-nav-list">
        <li>
          <button class="button" @click.prevent="isVisible = true">
            ✉️ Nous envoyer votre retour
          </button>
        </li>
        <li>
          <a href="https://iarbre.fr" class="my-link"> ⓘ En savoir plus </a>
        </li>
      </ul>
    </nav>
  </div>
  <FeedbackPopin v-if="isVisible" @submit-feedback="sendFeedbackToAPI" @close="isVisible = false" />
</template>
