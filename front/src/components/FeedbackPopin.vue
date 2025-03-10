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
    email.value = ""
    feedback.value = ""
  } else {
    message.value = "Veuillez remplir un avis."
  }
}
</script>

<template>
  <div
    class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 max-w-sm mx-auto p-5 border border-gray-300 rounded-lg bg-[var(--color-white)] text-[var(--color-dark-green)] text-left flex flex-col text-sm box-border"
  >
    <button
      class="button text absolute top-2 right-2 text-lg text-[var(--color-dark-green)] cursor-pointer transition-colors duration-300 hover:text-[var(--color-red)]"
      @click="emit('close')"
    >
      x
    </button>
    <h3 class="font-medium">Votre avis compte !</h3>
    <p class="mb-2">Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
    <form class="w-full" @submit="sendFeedback">
      <input
        v-model="email"
        type="email"
        placeholder="Votre email"
        required
        class="w-full mt-2 p-2 rounded-full border border-gray-300 outline-none"
      />
      <textarea
        v-model="feedback"
        placeholder="Votre message"
        required
        class="w-full h-36 mt-2 p-2 rounded-3xl border border-gray-300 resize-none outline-none"
      ></textarea>
      <button
        class="button w-full mt-2 bg-[var(--color-light-green)] text-[var(--color-white)] font-bold cursor-pointer transition-colors duration-300 hover:text-[var(--color-brown)] text-center"
        type="submit"
      >
        J'envoie mon avis
      </button>
      <p v-if="message" class="mt-2 text-[var(--color-dark-green)]">{{ message }}</p>
    </form>
  </div>
</template>
