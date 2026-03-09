import { nextTick } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useTutorialStore } from "@/stores/tutorial"
import { useAppStore } from "@/stores/app"
import { DriverButton, TutorialSelector } from "@/types/tutorial"
import type { AllowedButtons, DriveStep } from "driver.js"

type ClickAction = "nextStep" | "stopTutorial"
type ClickDelay = number | "nextTick" | undefined

const NAV_BUTTONS: AllowedButtons[] = [DriverButton.CLOSE, DriverButton.PREVIOUS, DriverButton.NEXT]

export function useTutorial() {
  const tutorialStore = useTutorialStore()
  const appStore = useAppStore()
  const route = useRoute()
  const router = useRouter()

  let overlayClickHandler: (() => void) | null = null

  const ensureMapPage = async () => {
    if (route.name !== "map") {
      await router.push({ name: "map" })
      await nextTick()
    }
  }

  const cleanupOverlayClick = () => {
    if (overlayClickHandler) {
      const overlay = document.querySelector(".driver-overlay")
      overlay?.removeEventListener("click", overlayClickHandler)
      overlayClickHandler = null
    }
  }

  const setupOverlayClickAdvance = () => {
    cleanupOverlayClick()
    const overlay = document.querySelector(".driver-overlay")
    if (overlay) {
      overlayClickHandler = () => {
        cleanupOverlayClick()
        tutorialStore.nextStep()
      }
      overlay.addEventListener("click", overlayClickHandler)
    }
  }

  const clickElement = (selector: string) => {
    const element = document.querySelector<HTMLElement>(selector)
    element?.click()
  }

  const onClickAdvance = (
    selector: string,
    action: ClickAction = "nextStep",
    delay: ClickDelay = undefined
  ) => {
    const element = document.querySelector(selector)
    const handleClick = () => {
      element?.removeEventListener("click", handleClick)
      cleanupOverlayClick()
      const execute = () =>
        action === "nextStep" ? tutorialStore.nextStep() : tutorialStore.stopTutorial()
      if (delay === "nextTick") nextTick(execute)
      else if (typeof delay === "number") setTimeout(execute, delay)
      else execute()
    }
    element?.addEventListener("click", handleClick)
  }

  const closeMobilePanel = () => {
    const panel = document.querySelector(".mobile-panel.is-open")
    if (panel) {
      clickElement(TutorialSelector.MOBILE_PANEL_HANDLE)
    }
  }

  const runTutorial = (steps: DriveStep[]) => {
    cleanupOverlayClick()
    closeMobilePanel()
    tutorialStore.startTutorial(steps)
  }

  const getMapSteps = (): DriveStep[] => {
    if (appStore.isMobileOrTablet) {
      return [
        {
          element: TutorialSelector.MAP_COMPONENT,
          popover: {
            title: "La carte interactive",
            description:
              "Cliquez n'importe où sur la carte pour obtenir des informations détaillées sur cette zone.",
            showButtons: NAV_BUTTONS
          },
          onHighlighted: () => onClickAdvance(TutorialSelector.MAP_COMPONENT, "nextStep", 500)
        },
        {
          element: TutorialSelector.MOBILE_PANEL,
          popover: {
            title: "Panneau de détails",
            description:
              "Les informations détaillées sur la zone sélectionnée s'affichent ici. Glissez vers le haut ou cliquez pour ouvrir le panneau.",
            showButtons: NAV_BUTTONS
          },
          onHighlighted: () => {
            clickElement(TutorialSelector.MOBILE_PANEL_HANDLE)
            setTimeout(() => {
              tutorialStore.driverInstance?.refresh()
              setupOverlayClickAdvance()
            }, 350)
          },
          onDeselected: () => {
            clickElement(TutorialSelector.MOBILE_PANEL_HANDLE)
          }
        }
      ]
    }
    return [
      {
        element: TutorialSelector.MAP_COMPONENT,
        popover: {
          title: "La carte interactive",
          description:
            "Cliquez n'importe où sur la carte pour obtenir des informations détaillées sur cette zone.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: () => onClickAdvance(TutorialSelector.MAP_COMPONENT)
      },
      {
        element: TutorialSelector.MAP_SIDE_PANEL,
        popover: {
          title: "Panneau d'informations",
          description: "Les informations détaillées sur la zone sélectionnée s'affichent ici.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    ]
  }

  const getLegendSteps = (): DriveStep[] => {
    return [
      {
        element: `${TutorialSelector.PLANTABILITY_LEGEND}, ${TutorialSelector.VULNERABILITY_LEGEND}, ${TutorialSelector.CLIMATE_ZONES_LEGEND}`,
        popover: {
          title: "La légende",
          description:
            "Cliquez sur les éléments de la légende pour filtrer et masquer certaines zones selon vos préférences.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    ]
  }

  const getToolSteps = (): DriveStep[] => {
    return [
      {
        element: TutorialSelector.MAP_GEOCODER,
        popover: {
          title: "Recherche",
          description: "Recherchez une adresse ou un lieu pour naviguer directement sur la carte.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      },
      {
        element: TutorialSelector.DRAWING_MODE_TOGGLE,
        popover: {
          title: "Outils de dessin",
          description:
            "Ouvrez la barre d'outils de dessin pour délimiter une zone personnalisée et obtenir des statistiques détaillées.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      },
      {
        element: TutorialSelector.BUTTON_3D,
        popover: {
          title: "Vue 3D",
          description:
            "Activez la vue 3D pour visualiser les bâtiments et le relief en trois dimensions.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    ]
  }

  const getLayerSwitcherSteps = (): DriveStep[] => {
    const isMobile = appStore.isMobileOrTablet
    return [
      {
        element: isMobile
          ? TutorialSelector.MOBILE_LAYER_SWITCHER
          : TutorialSelector.LAYER_SWITCHER,
        popover: {
          title: "Changement de calque",
          description:
            "Utilisez ce menu pour changer de calque et afficher différentes données sur la carte.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      },
      {
        element: TutorialSelector.MAP_BACKGROUND_SELECTOR,
        popover: {
          title: "Fond de carte",
          description: "Vous pouvez également changer le fond de carte (satellite, plan, etc.).",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    ]
  }

  const startMapTutorial = async () => {
    await ensureMapPage()
    runTutorial(getMapSteps())
  }

  const startLegendTutorial = async () => {
    await ensureMapPage()
    runTutorial(getLegendSteps())
  }

  const startLayerSwitcherTutorial = async () => {
    await ensureMapPage()
    runTutorial(getLayerSwitcherSteps())
  }

  const startFullTutorial = async () => {
    await ensureMapPage()
    const isMobile = appStore.isMobileOrTablet

    const steps: DriveStep[] = [
      ...getMapSteps(),
      ...getLegendSteps(),
      ...getLayerSwitcherSteps(),
      ...getToolSteps(),
      {
        element: isMobile
          ? TutorialSelector.DASHBOARD_BUTTON_MOBILE
          : TutorialSelector.DASHBOARD_BUTTON,
        popover: {
          title: "Tableau de bord",
          description:
            "Accédez au tableau de bord pour une vue synthétique de la métropole : plantabilité, îlots de chaleur, végétation et perméabilité.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      },
      {
        element: TutorialSelector.MAP_COMPONENT,
        popover: {
          title: "Tutoriel terminé",
          description: "Vous êtes prêt·e à explorer IA·rbre. Bonne découverte !",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    ]

    runTutorial(steps)
  }

  const startFeedbackTutorial = async () => {
    await ensureMapPage()
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.MOBILE_MENU_BUTTON,
        popover: {
          title: "Ouvrir le menu",
          description: "Cliquez sur le bouton menu pour accéder aux fonctionnalités.",
          showButtons: NAV_BUTTONS
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
        showButtons: NAV_BUTTONS
      },
      onHighlighted: () => onClickAdvance(TutorialSelector.OPEN_FEEDBACK_BUTTON, "stopTutorial")
    })

    runTutorial(steps)
  }

  return {
    startFullTutorial,
    startMapTutorial,
    startLegendTutorial,
    startLayerSwitcherTutorial,
    startFeedbackTutorial
  }
}
