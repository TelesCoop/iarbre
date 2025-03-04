<script lang="ts">
import { defineComponent, ref } from "vue";
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";

const slackWebhookUrl = import.meta.env.VITE_SLACK_WEBHOOK_URL;

export default defineComponent({
  setup() {
    const feedback = ref<string>("");
    const message = ref<string>("");
    const store = useFeedbackStore();

    const sendFeedback = async () => {
      if (!feedback.value.trim()) {
        message.value = "Veuillez écrire un avis avant d'envoyer.";
        return;
      }
      try {
        await axios.post(slackWebhookUrl, { text: feedback.value }, { headers: { "Content-Type": "application/json" } });
        message.value = "Merci pour votre avis !";
        feedback.value = "";
      } catch (error) {
        console.error("Erreur lors de l'envoi du feedback:", error);
        message.value = "Une erreur s'est produite, veuillez réessayer plus tard.";
      }
    };

    return {
      feedback,
      message,
      store,
      sendFeedback
    };
  }
});
</script>

<template>
    <div class="feedback-container" v-if="store.isVisible">
      <span class="close-btn" @click="store.hideFeedback">x</span>
      <p><strong>Votre avis compte !</strong></p>
      <p>Partagez-nous vos impressions pour nous aider à améliorer le site :</p>
      <textarea v-model="feedback" placeholder=""></textarea>
      <button @click="sendFeedback">J'envoie mon avis</button>
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </template>


<style lang="sass" scoped>
.feedback-container
  position: relative
  z-index: 1000 
  max-width: 400px
  margin: auto
  padding: 20px
  border: 1px solid #ccc
  border-radius: 5px
  background: $white
  color : $dark-green
  text-align: left
  display: flex
  flex-direction: column
  font-size: 0.9rem
  box-sizing: border-box

.close-btn
  position: absolute
  top: 10px
  right: 10px
  font-size: 18px
  color: $dark-green
  cursor: pointer
  transition: 0.3s
  &:hover
    color: red

textarea
  width: calc(100% - 20px)
  height: 150px
  margin-top: 10px
  padding: 10px
  border-radius: 20px
  border: 1px solid #ccc
  resize: none
  outline: none

button
  margin-top: 10px
  padding: 10px 26px
  border: none
  background-color: $light-green
  color: $white
  cursor: pointer
  border-radius: 20px
  width: 100%
  font-weight: bold
  transition: background 0.3s
  text-align: center
  font-family: 'Sligoil', sans-serif



.message
  margin-top: 10px
  color: $dark-green
</style>


