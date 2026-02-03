<script lang="ts" setup>
import { ref, onMounted, computed } from "vue"
import { LocalStorageHandler } from "@/utils/LocalStorageHandler"
import { useTutorial } from "@/composables/useTutorial"

interface welcomeProps {
  modelValue?: boolean
}

const props = withDefaults(defineProps<welcomeProps>(), {
  modelValue: undefined
})

const emit = defineEmits<{
  "update:modelValue": [value: boolean]
}>()

const tutorial = useTutorial()

const showWelcome = ref(false)

const isVisible = computed({
  get: () => (props.modelValue !== undefined ? props.modelValue : showWelcome.value),
  set: (value: boolean) => {
    if (props.modelValue !== undefined) {
      emit("update:modelValue", value)
    } else {
      showWelcome.value = value
    }
  }
})

onMounted(() => {
  if (props.modelValue === undefined) {
    const hasVisited = LocalStorageHandler.getItem("hasVisitedBefore")
    if (!hasVisited) {
      showWelcome.value = true
    }
  }
})

const closeWelcome = () => {
  isVisible.value = false
  if (props.modelValue === undefined) {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
  }
}

const startTutorialAndClose = (tutorialFn: () => void) => {
  closeWelcome()
  setTimeout(tutorialFn, 300)
}

const startTutorial = () => startTutorialAndClose(tutorial.startFullTutorial)
const startFeedbackTutorial = () => startTutorialAndClose(tutorial.startFeedbackTutorial)
</script>

<template>
  <Dialog
    v-model:visible="isVisible"
    :draggable="false"
    :style="{ width: '28rem' }"
    header="Bienvenue !"
    modal
    data-cy="welcome-dialog"
    :closable="true"
    :pt="{
      closeButton: {
        class: 'text-primary-500 hover:text-primary-700 hover:bg-transparent! transition-colors'
      }
    }"
  >
    <div class="flex flex-col gap-4 bg-white">
      <div class="space-y-4">
        <button
          class="welcome-functionnality welcome-functionnality--clickable w-full text-left"
          data-cy="welcome-map-tutorial"
          @click="startTutorial"
        >
          <span class="text-2xl">🗺️</span>
          <div>
            <h4 class="font-medium">Cliquez ici pour découvrir IA·rbre pas à pas</h4>
            <div class="space-y-1 mt-2">
              <li class="text-sm">Explorez la carte</li>
              <li class="text-sm">Utilisez la légende pour filtrer</li>
              <li class="text-sm">Changez de calque et de fond de carte</li>
            </div>
          </div>
        </button>

        <button
          class="welcome-functionnality welcome-functionnality--clickable w-full text-left"
          data-cy="welcome-feedback-tutorial"
          @click="startFeedbackTutorial"
        >
          <span class="text-2xl">💬</span>
          <div>
            <h4 class="font-medium">Donnez votre avis</h4>
            <p class="text-sm">
              en cliquant sur "Envoyer votre avis" pour partager vos commentaires.
            </p>
          </div>
        </button>

        <a
          href="https://iarbre.fr/#newsletter"
          target="_blank"
          class="welcome-functionnality welcome-functionnality--clickable w-full text-left"
        >
          <span class="text-2xl">✉️</span>
          <div>
            <h4 class="font-medium">En savoir plus</h4>
            <p class="text-sm">
              en vous abonnant à la
              <span class="text-primary-900 font-medium underline">newsletter</span>.
            </p>
          </div>
        </a>
      </div>
    </div>

    <template #footer>
      <Button label="Compris !" data-cy="welcome-click" class="w-full" @click="closeWelcome" />
    </template>
  </Dialog>
</template>
