import { ref } from "vue"
import { defineStore } from "pinia"
import { driver, type Driver, type DriveStep } from "driver.js"
import "driver.js/dist/driver.css"

export const useTutorialStore = defineStore("tutorial", () => {
  const driverInstance = ref<Driver | null>(null)
  const isActive = ref<boolean>(false)
  const currentStep = ref<number>(0)
  const totalSteps = ref<number>(0)

  const initDriver = (steps: DriveStep[]) => {
    if (driverInstance.value) {
      driverInstance.value.destroy()
    }

    driverInstance.value = driver({
      animate: true,
      overlayOpacity: 0.75,
      stagePadding: 10,
      allowClose: true,
      stageRadius: 5,
      showProgress: true,
      nextBtnText: "Suivant",
      prevBtnText: "Précédent",
      doneBtnText: "Terminer",
      progressText: "{{current}} sur {{total}}",
      allowKeyboardControl: true,
      onHighlightStarted: () => {
        isActive.value = true
      },
      onHighlighted: () => {
        currentStep.value = driverInstance.value?.getActiveIndex() || 0
      },
      onDestroyed: () => {
        isActive.value = false
        currentStep.value = 0
        totalSteps.value = 0
      },
      steps
    })

    return driverInstance.value
  }

  const startTutorial = (steps: DriveStep[]) => {
    const instance = initDriver(steps)
    if (!instance) return

    totalSteps.value = steps.length
    instance.drive()
  }

  const nextStep = () => {
    if (driverInstance.value) {
      driverInstance.value.moveNext()
    }
  }

  const previousStep = () => {
    if (driverInstance.value) {
      driverInstance.value.movePrevious()
    }
  }

  const stopTutorial = () => {
    if (driverInstance.value) {
      driverInstance.value.destroy()
    }
  }

  const isTutorialActive = () => isActive.value

  const getCurrentStep = () => currentStep.value
  const getTotalSteps = () => totalSteps.value

  return {
    driverInstance,
    isActive,
    currentStep,
    totalSteps,
    startTutorial,
    nextStep,
    previousStep,
    stopTutorial,
    isTutorialActive,
    getCurrentStep,
    getTotalSteps
  }
})
