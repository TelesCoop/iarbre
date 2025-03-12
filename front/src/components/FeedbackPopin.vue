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
  <div class="my-popin" data-cy="feedback-popin">
    <button class="my-popin-close-button" @click="emit('close')">x</button>
    <h3 class="my-popin-heading">Votre avis compte !</h3>
    <p class="my-popin-text">Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
    <form class="my-popin-form" @submit="sendFeedback">
      <input v-model="email" type="email" placeholder="Votre email" class="my-input" />
      <textarea v-model="feedback" placeholder="Votre message" class="my-textarea"></textarea>
      <button class="my-submit-button" type="submit">J'envoie mon avis</button>
      <p v-if="message" class="my-message">{{ message }}</p>
    </form>
  </div>
</template>
