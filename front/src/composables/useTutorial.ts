import { nextTick } from "vue"
import { useTutorialStore } from "@/stores/tutorial"
import { useAppStore } from "@/stores/app"
import { DriverButton, TutorialSelector } from "@/types/tutorial"
import type { DriveStep } from "driver.js"

type ClickAction = "nextStep" | "stopTutorial"
type ClickDelay = number | "nextTick" | undefined

export function useTutorial() {
  const tutorialStore = useTutorialStore()
  const appStore = useAppStore()

  const onClickAdvance = (
    selector: string,
    action: ClickAction = "nextStep",
    delay: ClickDelay = undefined
  ) => {
    const element = document.querySelector(selector)
    const handleClick = () => {
      element?.removeEventListener("click", handleClick)
      const execute = () =>
        action === "nextStep" ? tutorialStore.nextStep() : tutorialStore.stopTutorial()
      if (delay === "nextTick") nextTick(execute)
      else if (typeof delay === "number") setTimeout(execute, delay)
      else execute()
    }
    element?.addEventListener("click", handleClick)
  }

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
        onHighlighted: () => onClickAdvance(TutorialSelector.MAP_COMPONENT, "nextStep", 500)
      },
      {
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau",
          description: "Cliquez ici pour afficher les informations détaillées.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => onClickAdvance(TutorialSelector.DRAWER_TOGGLE, "nextStep", "nextTick")
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
        onHighlighted: () => onClickAdvance(TutorialSelector.MAP_COMPONENT)
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
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau de configuration",
          description:
            "Cliquez ici pour ouvrir le panneau de configuration et accéder à la légende.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => onClickAdvance(TutorialSelector.DRAWER_TOGGLE, "nextStep", "nextTick")
      })
    }

    steps.push(
      {
        element: `${TutorialSelector.PLANTABILITY_LEGEND}, ${TutorialSelector.VULNERABILITY_LEGEND}, ${TutorialSelector.CLIMATE_ZONES_LEGEND}`,
        popover: {
          title: "La légende",
          description:
            "Cliquez sur les éléments de la légende pour filtrer et masquer certaines zones selon vos préférences.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => {
          const legends = [
            TutorialSelector.PLANTABILITY_LEGEND,
            TutorialSelector.VULNERABILITY_LEGEND,
            TutorialSelector.CLIMATE_ZONES_LEGEND
          ].map((s) => document.querySelector(s))

          const handleLegendClick = (event: Event) => {
            const target = event.target as HTMLElement
            const hasFilterAttr =
              target.hasAttribute("data-score") ||
              target.hasAttribute("data-zone") ||
              target.hasAttribute("data-climate-zone")

            if (hasFilterAttr && document.querySelector(TutorialSelector.MAP_FILTERS_STATUS)) {
              legends.forEach((el) => el?.removeEventListener("click", handleLegendClick))
              tutorialStore.nextStep()
            }
          }

          legends.forEach((el) => el?.addEventListener("click", handleLegendClick))
        }
      },
      {
        element: TutorialSelector.MAP_FILTERS_STATUS,
        popover: {
          title: "Filtres actifs",
          description:
            "Vous pouvez voir ici les filtres actuellement appliqués. Vous pouvez cliquer sur effacer pour supprimer tous les filtres."
        }
      }
    )

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.DRAWER_CLOSE_BUTTON,
        popover: {
          title: "Fermer le panneau",
          description: "Cliquez sur la croix pour fermer le panneau de configuration.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () =>
          onClickAdvance(TutorialSelector.DRAWER_CLOSE_BUTTON, "nextStep", "nextTick")
      })
    }

    steps.push({
      element: TutorialSelector.MAP_COMPONENT,
      popover: {
        title: "Visualisation des filtres",
        description:
          "La carte affiche maintenant uniquement les zones correspondant à vos filtres. Vous pouvez continuer à explorer ou modifier vos filtres à tout moment."
      }
    })

    startTutorial(steps)
  }

  const startLayerSwitcherTutorial = () => {
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau de configuration",
          description:
            "Cliquez ici pour ouvrir le panneau de configuration et accéder aux options de calques.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () => onClickAdvance(TutorialSelector.DRAWER_TOGGLE, "nextStep", "nextTick")
      })
    }

    steps.push(
      {
        element: TutorialSelector.LAYER_SWITCHER,
        popover: {
          title: "Changement de calque",
          description:
            "Utilisez ce menu pour changer de calque et afficher différentes données sur la carte.",
          showButtons: [DriverButton.CLOSE, DriverButton.NEXT]
        }
      },
      {
        element: TutorialSelector.MAP_BG_SWITCHER,
        popover: {
          title: "Fond de carte",
          description: "Vous pouvez également changer le fond de carte (satellite, plan, etc.)."
        }
      }
    )

    startTutorial(steps)
  }

  const startFeedbackTutorial = () => {
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.MOBILE_MENU_BUTTON,
        popover: {
          title: "Ouvrir le menu",
          description: "Cliquez sur le bouton menu pour accéder aux fonctionnalités.",
          showButtons: [DriverButton.CLOSE]
        },
        onHighlighted: () =>
          onClickAdvance(TutorialSelector.MOBILE_MENU_BUTTON, "nextStep", "nextTick")
      })
    }

    steps.push({
      element: TutorialSelector.OPEN_FEEDBACK_BUTTON,
      popover: {
        title: "Donnez votre avis",
        description:
          "Cliquez ici pour partager vos commentaires et nous aider à améliorer la plateforme.",
        showButtons: [DriverButton.CLOSE]
      },
      onHighlighted: () => onClickAdvance(TutorialSelector.OPEN_FEEDBACK_BUTTON, "stopTutorial")
    })

    startTutorial(steps)
  }

  return {
    startTutorial,
    startMapTutorial,
    startLegendTutorial,
    startLayerSwitcherTutorial,
    startFeedbackTutorial
  }
}
