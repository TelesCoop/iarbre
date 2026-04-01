<script lang="ts" setup>
import { ref, computed } from "vue"
import FeedbackForm from "@/components/forms/FeedbackForm.vue"
import AppDialog from "@/components/shared/AppDialog.vue"

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  "update:modelValue": [value: boolean]
  "submit-feedback": [data: { email: string; feedback: string }]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value)
})

const email = ref("")
const feedback = ref("")
</script>

<template>
  <AppDialog
    v-model:visible="visible"
    :draggable="false"
    width="25rem"
    data-cy="feedback-popin"
    header="Votre avis compte !"
    modal
  >
    <FeedbackForm
      :email="email"
      :feedback="feedback"
      @submit-feedback="emit('submit-feedback', { email: $event.email, feedback: $event.feedback })"
    />
  </AppDialog>
</template>
