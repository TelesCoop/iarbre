<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"
import { FULL_BASE_API_URL } from "@/utils/constants"

const isVisible = ref(false)
const feedback = ref<string>("")
const message = ref<string>("")
const email = ref<string>("")

const showFeedback = () => {
  isVisible.value = true
}

const hideFeedback = () => {
  isVisible.value = false
}

const sendFeedback = async () => {
  if (!feedback.value.trim()) {
    message.value = "Veuillez écrire un avis avant d'envoyer."
    return
  }
  try {
    await axios.post(
      `${FULL_BASE_API_URL}/feedback/`,
      { feedback: feedback.value, email: email.value },
      { headers: { "Content-Type": "application/json" } }
    )
    message.value = "Merci pour votre avis !"
    feedback.value = ""
    email.value = ""
  } catch (error) {
    console.error("Erreur lors de l'envoi du feedback:", error)
    message.value = "Une erreur s'est produite, veuillez réessayer plus tard."
  }
}
</script>

<template>
  <div class="layout">
    <header class="navbar">
      <div class="navbar-left">
        <a href="/">
          <img class="navbar-logo" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
        </a>
      </div>
      <nav class="navbar-right">
        <ul>
          <li>
            <a href="#" class="navbar-link" @click.prevent="showFeedback">
              ✉️ Nous envoyer votre retour
            </a>
          </li>
          <li><a href="https://iarbre.fr" class="navbar-link">ⓘ En savoir plus</a></li>
        </ul>
      </nav>
    </header>

    <main class="default-content">
      <slot></slot>
    </main>

    <!-- Feedback -->
    <div v-if="isVisible" class="feedback-container">
      <span class="close-btn" @click="hideFeedback">x</span>
      <p><strong>Votre avis compte !</strong></p>
      <p>Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
      <input v-model="email" type="email" placeholder="Votre email" />
      <textarea v-model="feedback" placeholder="Votre message"></textarea>
      <button @click="sendFeedback">J'envoie mon avis</button>
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
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

    &:hover
      color: $light-green


.layout
  display: flex
  flex-direction: column
  min-height: 100vh

.default-content
  min-height: $content-height
  margin-top: $header-height
  flex: 1

.feedback-container
  position: fixed
  top: 50%
  left: 50%
  transform: translate(-50%, -50%)
  z-index: 1000
  max-width: 400px
  margin: auto
  padding: 20px
  border: 1px solid #ccc
  border-radius: 5px
  background: $white
  color : $dark-green
  text-align: left
  display: flex
  flex-direction: column
  font-size: 0.9rem
  box-sizing: border-box

.close-btn
  position: absolute
  top: 10px
  right: 10px
  font-size: 18px
  color: $dark-green
  cursor: pointer
  transition: 0.3s
  &:hover
    color: red

textarea
  width: calc(100% - 20px)
  height: 150px
  margin-top: 10px
  padding: 10px
  border-radius: 20px
  border: 1px solid #ccc
  resize: none
  outline: none

input
  width: calc(100% - 10px)
  margin-top: 10px
  padding: 5px
  border-radius: 20px
  border: 1px solid #ccc
  outline: none

button
  margin-top: 10px
  padding: 10px 26px
  border: none
  background-color: $light-green
  color: $white
  cursor: pointer
  border-radius: 20px
  width: 100%
  font-weight: bold
  transition: background 0.3s
  text-align: center
  font-family: 'Sligoil', sans-serif



.message
  margin-top: 10px
  color: $dark-green
</style>
