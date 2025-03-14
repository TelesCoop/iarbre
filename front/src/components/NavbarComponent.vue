<script setup lang="ts">
import { ref } from "vue"
import { useApiPost } from "@/api"
import FeedbackPopin from "@/components/FeedbackPopin.vue"
import type { Feedback } from "@/types"

const isVisible = ref(false)

const sendFeedbackToAPI = async (data: Feedback) => {
  const { error } = await useApiPost<Feedback>("feedback", data)
  if (error != null) {
    console.log("l12 error")
    return false
  }
  console.log("l15")
  isVisible.value = false
  return true
}
</script>

<template>
  <div class="header">
    <div class="header-logo">
      <a href="/">
        <img class="h-10 w-auto" src="/images/logo-iarbre.png" alt="Logo I-Arbre" />
      </a>
    </div>
    <nav class="header-nav">
      <ul class="nav-list">
        <li>
          <button class="button" data-cy="open-feedback-button" @click.prevent="isVisible = true">
            ✉️ Nous envoyer votre retour {{ isVisible }}
          </button>
        </li>
        <li>
          <a href="https://iarbre.fr" class="link" data-cy="open-savoir-href"> ⓘ En savoir plus </a>
        </li>
      </ul>
    </nav>
  </div>
  <FeedbackPopin v-if="isVisible" @submit-feedback="sendFeedbackToAPI" @close="isVisible = false" />
</template>
