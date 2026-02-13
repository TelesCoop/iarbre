<script lang="ts" setup>
import { ref } from "vue"

const props = defineProps({
  email: {
    type: String,
    default: ""
  },
  feedback: {
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
    <span class="popin-text"
      >Partagez-nous vos impressions pour nous aider à améliorer le site :</span
    >
    <input v-model="email" class="form-input" placeholder="Votre email" type="email" />
    <textarea
      v-model="feedback"
      class="form-textarea"
      cols="30"
      placeholder="Votre message"
      required
      rows="5"
    />
    <AppButton data-cy="submit-feedback-button" variant="secondary" type="submit" full-width>
      J'envoie mon avis
    </AppButton>
  </form>
</template>

<style scoped>
@reference "@/styles/main.css";

.popin-form {
  @apply w-full flex flex-col gap-4;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-500;
  @apply placeholder-gray-400;
}

.form-textarea {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-500;
  @apply placeholder-gray-400;
}
</style>
