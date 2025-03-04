import { defineStore } from "pinia"
import { ref } from "vue"

export const useFeedbackStore = defineStore("feedback", () => {
  const isVisible = ref(false)

  const showFeedback = () => {
    isVisible.value = true
  }

  const hideFeedback = () => {
    isVisible.value = false
  }

  return { isVisible, showFeedback, hideFeedback }
})
