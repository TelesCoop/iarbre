<script lang="ts" setup>
import { ref, computed } from "vue"
import FeedbackForm from "@/components/forms/FeedbackForm.vue"
import AppDialog from "@/components/shared/AppDialog.vue"

const modelValue = defineModel({
  type: Boolean,
  required: true
})

const visible = computed({
  get: () => modelValue.value,
  set: (value: boolean) => {
    modelValue.value = value
  }
})

const email = ref("")
const feedback = ref("")
const emit = defineEmits(["submit-feedback", "close"])
</script>

<template>
  <AppDialog
    v-model:visible="visible"
    :draggable="false"
    width="25rem"
    data-cy="feedback-popin"
    header="Votre avis compte !"
    modal
    @hide="emit('close')"
  >
    <FeedbackForm
      :email="email"
      :feedback="feedback"
      @submit-feedback="emit('submit-feedback', { email: $event.email, feedback: $event.feedback })"
    />
  </AppDialog>
</template>
