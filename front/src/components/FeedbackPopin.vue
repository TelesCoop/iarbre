<script setup lang="ts">
import { ref } from "vue"
import FeedbackForm from "@/components/forms/FeedbackForm.vue"

const props = defineProps({
  message: {
    required: true,
    type: String
  }
})

const email = ref("")
const feedback = ref("")

const emit = defineEmits(["submit-feedback", "close"])
</script>

<template>
  <div class="popin" data-cy="feedback-popin">
    <button class="popin-close-button" data-cy="close-feedback-button" @click="emit('close')">
      x
    </button>
    <h3 class="popin-heading">Votre avis compte !</h3>
    <p class="popin-text">Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
    <feedback-form
      :email="email"
      :feedback="feedback"
      :message="props.message"
      @submit-feedback="emit('submit-feedback', { email: $event.email, feedback: $event.feedback })"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.popin {
  @apply fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 max-w-sm mx-auto p-5 border border-gray-300 rounded-lg bg-white text-dark-green text-left flex flex-col text-sm box-border;
}

.popin-close-button {
  @apply absolute top-2 right-2 text-lg text-dark-green cursor-pointer transition-colors duration-300 hover:text-red-500;
}

.popin-heading {
  @apply font-medium;
}

.popin-text {
  @apply mb-2;
}
</style>
