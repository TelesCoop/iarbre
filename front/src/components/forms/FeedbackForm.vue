<script setup lang="ts">
import { ref } from "vue"

const props = defineProps({
  email: {
    type: String,
    default: ""
  },
  feedback: {
    type: String,
    default: ""
  },
  message: {
    type: String,
    default: ""
  }
})

const email = ref(props.email)
const feedback = ref(props.feedback)
const emit = defineEmits(["submit-feedback"])

const sendFeedback = (event: Event) => {
  event.preventDefault()
  emit("submit-feedback", { email: email.value, feedback: feedback.value })
}
</script>

<template>
  <form class="popin-form" @submit="sendFeedback">
    <input v-model="email" type="email" placeholder="Votre email" class="feedback-input" />
    <textarea v-model="feedback" placeholder="Votre message" class="feedback-textarea"></textarea>
    <button class="feedback-submit-button" type="submit" data-cy="submit-feedback-button">
      J'envoie mon avis
    </button>
    <p v-if="message" class="message">{{ message }}</p>
  </form>
</template>

<style scoped>
@reference "@/styles/main.css";

.popin-form {
  @apply w-full;
}

.feedback-input {
  @apply w-full mt-2 p-2 rounded-full border border-gray-300 outline-none;
}

.feedback-textarea {
  @apply w-full h-36 mt-2 p-2 rounded-3xl border border-gray-300 resize-none outline-none;
}

.feedback-submit-button {
  @apply w-full mt-2 bg-light-green text-white font-bold cursor-pointer transition-colors duration-300 hover:text-white text-center rounded-full py-2;
}

.message {
  @apply mt-2 text-dark-green;
}
</style>
