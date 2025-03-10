<script setup lang="ts">
import { ref } from "vue"
import { FULL_BASE_API_URL } from "@/utils/constants"
import FeedbackPopin from "@/components/FeedbackPopin.vue"

const isVisible = ref(false)

const emit = defineEmits(["show-toast"])

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

    emit("show-toast", { type: "success", message: "Merci pour votre avis !" })
    isVisible.value = false
  } catch (error) {
    console.error("Erreur lors de l'envoi du feedback:", error)
    emit("show-toast", {
      type: "error",
      message: "Une erreur s'est produite. Merci de recommencer plus tard."
    })
  }
}
</script>

<template>
  <div class="navbar">
    <div class="navbar-left">
      <a href="/">
        <img class="navbar-logo" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </a>
    </div>
    <nav class="navbar-right">
      <ul>
        <li>
          <button class="navbar-link" @click.prevent="isVisible = true">
            ✉️ Nous envoyer votre retour
          </button>
        </li>
        <li><a href="https://iarbre.fr" class="navbar-link">ⓘ En savoir plus</a></li>
      </ul>
    </nav>
  </div>
  <FeedbackPopin
    v-if="isVisible"
    @submit-feedback="sendFeedbackToAPI"
    @on-close="isVisible = false"
  />
</template>

<style scoped lang="sass">
.navbar
  background-color: $off-white
  height: $header-height
  position: fixed
  width: 100%
  top: 0
  z-index: 2
  box-sizing: border-box
  overflow: hidden

  display: flex
  align-items: center
  justify-content: space-between
  padding: 10px 40px

  .navbar-logo
    height: 40px
    width: auto

  .navbar-right
    ul
      list-style: none
      display: flex
      gap: 1.1rem
      flex-direction: horizontal

  .navbar-link
    font-family: $accent-font, Arial, sans-serif
    color: $brown
    text-decoration: none
    font-size: 1rem
    transition: color 0.3s ease
    background-color: $off-white
    border: none
    outline: none

    &:hover
      color: $light-green
</style>
