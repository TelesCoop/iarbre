<script lang="ts" setup>
import { ref } from "vue"
import FeedbackForm from "@/components/forms/FeedbackForm.vue"
import Dialog from "primevue/dialog"

const visible = defineModel({
  type: Boolean,
  required: true
})
const email = ref("")
const feedback = ref("")
const emit = defineEmits(["submit-feedback", "close"])
</script>

<template>
  <Dialog
    v-model:visible="visible"
    :draggable="false"
    :style="{ width: '25rem' }"
    data-cy="feedback-popin"
    header="Votre avis compte !"
    modal
    @hide="emit('close')"
  >
    <feedback-form
      :email="email"
      :feedback="feedback"
      @submit-feedback="emit('submit-feedback', { email: $event.email, feedback: $event.feedback })"
    />
  </Dialog>
</template>
