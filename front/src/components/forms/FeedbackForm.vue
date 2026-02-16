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
const consent = ref(false)
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
    <label class="consent-label">
      <input v-model="consent" type="checkbox" class="consent-checkbox" />
      <span class="consent-text">
        J'accepte que mes données soient traitées conformément à la
        <a href="/mentions-legales" target="_blank" rel="noopener noreferrer" class="consent-link">
          politique de confidentialité</a
        >.
      </span>
    </label>
    <AppButton
      data-cy="submit-feedback-button"
      variant="secondary"
      type="submit"
      full-width
      :disabled="!consent"
    >
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

.consent-label {
  @apply flex items-start gap-2 cursor-pointer;
}

.consent-checkbox {
  @apply mt-0.5 shrink-0 accent-primary-500;
}

.consent-text {
  @apply text-xs text-gray-600 leading-relaxed;
}

.consent-link {
  @apply text-primary-500 underline;
  @apply hover:text-primary-600;
}
</style>
