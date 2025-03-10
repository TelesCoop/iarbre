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
  <div
    class="fixed top-0 w-full bg-[var(--color-off-white)] h-[var(--header-height)] z-10 flex items-center justify-between overflow-hidden box-border"
  >
    <div class="pl-4 md:pl-0">
      <a href="/">
        <img class="h-10 w-auto" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </a>
    </div>
    <nav class="pr-4 md:pr-20">
      <ul class="flex gap-4 list-none">
        <li>
          <button
            class="font-[var(--font-accent)] text-[var(--color-brown)] text-base bg-[var(--color-off-white)] border-none outline-none transition duration-300 hover:text-[var(--color-light-green)] cursor-pointer"
            @click.prevent="isVisible = true"
          >
            ✉️ Nous envoyer votre retour
          </button>
        </li>
        <li>
          <a
            href="https://iarbre.fr"
            class="font-[var(--font-accent)] text-[var(--color-brown)] text-base no-underline transition duration-300 hover:text-[var(--color-light-green)]"
          >
            ⓘ En savoir plus
          </a>
        </li>
      </ul>
    </nav>
  </div>
  <FeedbackPopin v-if="isVisible" @submit-feedback="sendFeedbackToAPI" @close="isVisible = false" />
</template>
