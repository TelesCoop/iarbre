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
    <InputText v-model="email" class="w-full" placeholder="Votre email" required type="email" />
    <Textarea
      v-model="feedback"
      class="w-full"
      cols="30"
      placeholder="Votre message"
      required
      rows="5"
    />
    <Button
      class="w-full"
      data-cy="submit-feedback-button"
      label="J'envoie mon avis"
      severity="secondary"
      type="submit"
    />
  </form>
</template>

<style scoped>
@reference "@/styles/main.css";

.popin-form {
  @apply w-full;
  @apply flex flex-col gap-4;
}
</style>
