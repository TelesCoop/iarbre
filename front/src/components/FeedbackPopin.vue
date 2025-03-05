<script setup lang="ts">
import { ref, defineEmits } from "vue"

const email = ref("")
const feedback = ref("")
const message = ref("")

const emit = defineEmits(["submit-feedback", "on-close"])

const sendFeedback = (event: Event) => {
  event.preventDefault()

  if (feedback.value) {
    emit("submit-feedback", { email: email.value, feedback: feedback.value })
    email.value = ""
    feedback.value = ""
  } else {
    message.value = "Veuillez remplir un avis."
  }
}
</script>

<template>
  <div class="feedback-container">
    <button class="button text close-btn" @click="emit('on-close')">x</button>
    <h3>Votre avis compte !</h3>
    <p>Partagez-nous vos impressions pour nous aider à améliorer le site :</p>

    <form @submit="sendFeedback">
      <input v-model="email" type="email" placeholder="Votre email" required />
      <textarea v-model="feedback" placeholder="Votre message" required></textarea>
      <button class="button send-btn" type="submit">J'envoie mon avis</button>
      <p v-if="message" class="message">{{ message }}</p>
    </form>
  </div>
</template>

<style scoped lang="sass">
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
    color: $red

.send-btn
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
  &:hover
    color: $brown

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





.message
  margin-top: 10px
  color: $dark-green
</style>
