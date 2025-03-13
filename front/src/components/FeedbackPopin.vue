<script setup lang="ts">
import { ref, defineEmits } from "vue"

const email = ref("")
const feedback = ref("")
const message = ref("")

const emit = defineEmits(["submit-feedback", "close"])

const sendFeedback = (event: Event) => {
  event.preventDefault()

  if (feedback.value) {
    emit("submit-feedback", { email: email.value, feedback: feedback.value })
    message.value = "Merci pour votre retour !"
    email.value = ""
    feedback.value = ""
    setTimeout(() => {
      emit("close")
    }, 1500)
  } else {
    message.value = "Veuillez remplir un avis."
  }
}
</script>

<template>
  <div class="popin" data-cy="feedback-popin">
    <button class="popin-close-button" data-cy="close-feedback-button" @click="emit('close')">
      x
    </button>
    <h3 class="popin-heading">Votre avis compte !</h3>
    <p class="popin-text">Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
    <form class="popin-form" @submit="sendFeedback">
      <input v-model="email" type="email" placeholder="Votre email" class="feedback-input" />
      <textarea v-model="feedback" placeholder="Votre message" class="feedback-textarea"></textarea>
      <button class="feedback-submit-button" type="submit" data-cy="submit-feedback-button">
        J'envoie mon avis
      </button>
      <p v-if="message" class="message">{{ message }}</p>
    </form>
  </div>
</template>
