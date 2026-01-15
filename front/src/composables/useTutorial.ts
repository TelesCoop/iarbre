import { nextTick } from "vue"
import { useTutorialStore } from "@/stores/tutorial"
import { Drawer, useAppStore } from "@/stores/app"
import { DriverButton, TutorialSelector } from "@/types/tutorial"
import type { DriveStep } from "driver.js"

export function useTutorial() {
  const tutorialStore = useTutorialStore()
  const appStore = useAppStore()

  const startTutorial = (steps: DriveStep[]) => {
    tutorialStore.startTutorial(steps)
  }

  const startMapTutorialMobile = () => {
    startTutorial([
      {
        element: TutorialSelector.MAP_COMPONENT,
        popover: {
          title: "La carte interactive",
          description:
            "Cliquez n'importe où sur la carte pour obtenir des informations détaillées sur cette zone.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => {
          const mapElement = document.querySelector(TutorialSelector.MAP_COMPONENT)
          const handleMapClick = () => {
            mapElement?.removeEventListener("click", handleMapClick)
            // Wait for data to load before showing next step
            setTimeout(() => {
              tutorialStore.nextStep()
            }, 500)
          }
          mapElement?.addEventListener("click", handleMapClick)
        }
      },
      {
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau",
          description: "Cliquez ici pour afficher les informations détaillées.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => {
          const toggleElement = document.querySelector(TutorialSelector.DRAWER_TOGGLE)
          const handleToggleClick = () => {
            toggleElement?.removeEventListener("click", handleToggleClick)
            nextTick(() => {
              tutorialStore.nextStep()
            })
          }
          toggleElement?.addEventListener("click", handleToggleClick)
        }
      },
      {
        element: TutorialSelector.MAP_CONFIG_DRAWER,
        popover: {
          title: "Panneau d'informations",
          description: "Les informations détaillées sur la zone sélectionnée s'affichent ici.",
          showButtons: [DriverButton.CLOSE, DriverButton.NEXT]
        }
      }
    ])
  }

  const startMapTutorialDesktop = () => {
    startTutorial([
      {
        element: TutorialSelector.MAP_COMPONENT,
        popover: {
          title: "La carte interactive",
          description:
            "Cliquez n'importe où sur la carte pour obtenir des informations détaillées sur cette zone.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => {
          const mapElement = document.querySelector(TutorialSelector.MAP_COMPONENT)
          const handleMapClick = () => {
            mapElement?.removeEventListener("click", handleMapClick)
            tutorialStore.nextStep()
          }
          mapElement?.addEventListener("click", handleMapClick)
        }
      },
      {
        element: TutorialSelector.MAP_SIDE_PANEL,
        popover: {
          title: "Panneau d'informations",
          description: "Les informations détaillées sur la zone sélectionnée s'affichent ici."
        }
      }
    ])
  }

  const startMapTutorial = () => {
    if (appStore.isMobileOrTablet) {
      startMapTutorialMobile()
    } else {
      startMapTutorialDesktop()
    }
  }

  const startLegendTutorial = () => {
    startTutorial([
      {
        element: `${TutorialSelector.PLANTABILITY_LEGEND}, ${TutorialSelector.VULNERABILITY_LEGEND}`,
        popover: {
          title: "La légende",
          description:
            "Cliquez sur les éléments de la légende pour filtrer et masquer certaines zones selon vos préférences."
        }
      }
    ])
  }

  const startLayerSwitcherTutorial = () => {
    startTutorial([
      {
        element: TutorialSelector.LAYER_SWITCHER,
        popover: {
          title: "Changement de calque",
          description:
            "Utilisez ce menu pour changer de calque et afficher différentes données sur la carte."
        }
      },
      {
        element: TutorialSelector.MAP_BG_SWITCHER,
        popover: {
          title: "Fond de carte",
          description: "Vous pouvez également changer le fond de carte (satellite, plan, etc.)."
        }
      }
    ])
  }

  const startFeedbackTutorial = () => {
    startTutorial([
      {
        element: TutorialSelector.OPEN_FEEDBACK_BUTTON,
        popover: {
          title: "Donnez votre avis",
          description:
            "Cliquez ici pour partager vos commentaires et nous aider à améliorer la plateforme."
        }
      }
    ])
  }

  return {
    startTutorial,
    startMapTutorial,
    startLegendTutorial,
    startLayerSwitcherTutorial,
    startFeedbackTutorial
  }
}
