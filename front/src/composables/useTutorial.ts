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
        element: `${TutorialSelector.PLANTABILITY_LEGEND}, ${TutorialSelector.VULNERABILITY_LEGEND}, ${TutorialSelector.CLIMATE_ZONES_LEGEND}`,
        popover: {
          title: "La légende",
          description:
            "Cliquez sur les éléments de la légende pour filtrer et masquer certaines zones selon vos préférences.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => {
          // Add event listener to legend items to detect when user clicks on them
          const plantabilityLegend = document.querySelector(TutorialSelector.PLANTABILITY_LEGEND)
          const vulnerabilityLegend = document.querySelector(TutorialSelector.VULNERABILITY_LEGEND)
          const climateZonesLegend = document.querySelector(TutorialSelector.CLIMATE_ZONES_LEGEND)

          const handleLegendClick = (event: Event) => {
            // Check if the click was on a legend item (score, zone, or climate zone)
            const target = event.target as HTMLElement
            if (
              target.hasAttribute("data-score") ||
              target.hasAttribute("data-zone") ||
              target.hasAttribute("data-climate-zone")
            ) {
              // Remove event listeners to prevent multiple triggers
              plantabilityLegend?.removeEventListener("click", handleLegendClick)
              vulnerabilityLegend?.removeEventListener("click", handleLegendClick)
              climateZonesLegend?.removeEventListener("click", handleLegendClick)

              // Wait for the filter status to appear and check if it exists
              const checkFilterStatus = () => {
                const filterStatus = document.querySelector(TutorialSelector.MAP_FILTERS_STATUS)
                if (filterStatus) {
                  tutorialStore.nextStep()
                } else {
                  // If filter status doesn't appear, try again after a short delay
                  setTimeout(checkFilterStatus, 100)
                }
              }

              // Start checking for filter status after a brief delay
              setTimeout(checkFilterStatus, 500)
            }
          }

          plantabilityLegend?.addEventListener("click", handleLegendClick)
          vulnerabilityLegend?.addEventListener("click", handleLegendClick)
          climateZonesLegend?.addEventListener("click", handleLegendClick)
        }
      },
      {
        element: TutorialSelector.MAP_FILTERS_STATUS,
        popover: {
          title: "Filtres actifs",
          description:
            "Vous pouvez voir ici les filtres actuellement appliqués. Vous pouvez cliquer sur effacer pour supprimer tous les filtres."
        }
      },
      {
        element: TutorialSelector.MAP_COMPONENT,
        popover: {
          title: "Visualisation des filtres",
          description:
            "La carte affiche maintenant uniquement les zones correspondant à vos filtres. Vous pouvez continuer à explorer ou modifier vos filtres à tout moment."
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
