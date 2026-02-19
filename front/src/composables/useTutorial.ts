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
  const router = useRouter()
  const route = useRoute()

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

  const createLegendClickHandler = () => {
    setupOverlayClickAdvance()
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
        cleanupOverlayClick()
        tutorialStore.nextStep()
      }
    }

    legends.forEach((el) => el?.addEventListener("click", handleLegendClick))
  }

  const runTutorial = (steps: DriveStep[]) => {
    cleanupOverlayClick()
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
          element: TutorialSelector.DRAWER_TOGGLE,
          popover: {
            title: "Ouvrir le panneau",
            description: "Cliquez ici pour afficher les informations détaillées.",
            showButtons: NAV_BUTTONS
          },
          onHighlighted: () =>
            onClickAdvance(TutorialSelector.DRAWER_TOGGLE, "nextStep", "nextTick")
        },
        {
          element: TutorialSelector.MAP_CONFIG_DRAWER,
          popover: {
            title: "Panneau d'informations",
            description: "Les informations détaillées sur la zone sélectionnée s'affichent ici.",
            showButtons: NAV_BUTTONS
          },
          onHighlighted: setupOverlayClickAdvance
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

  const getLegendSteps = (options?: { skipOpenDrawer?: boolean }): DriveStep[] => {
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet && !options?.skipOpenDrawer) {
      steps.push({
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau de configuration",
          description:
            "Cliquez ici pour ouvrir le panneau de configuration et accéder à la légende.",
          showButtons: NAV_BUTTONS
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
          showButtons: NAV_BUTTONS
        },
        onHighlighted: createLegendClickHandler
      },
      {
        element: TutorialSelector.MAP_FILTERS_STATUS,
        popover: {
          title: "Filtres actifs",
          description:
            "Vous pouvez voir ici les filtres actuellement appliqués. Vous pouvez cliquer sur effacer pour supprimer tous les filtres.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: setupOverlayClickAdvance
      }
    )

    return steps
  }

  const getLegendCloseSteps = (): DriveStep[] => {
    const steps: DriveStep[] = []

    if (appStore.isMobileOrTablet) {
      steps.push({
        element: TutorialSelector.DRAWER_CLOSE_BUTTON,
        popover: {
          title: "Fermer le panneau",
          description: "Cliquez sur la croix pour fermer le panneau de configuration.",
          showButtons: NAV_BUTTONS
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
          "La carte affiche maintenant uniquement les zones correspondant à vos filtres. Vous pouvez continuer à explorer ou modifier vos filtres à tout moment.",
        showButtons: NAV_BUTTONS
      },
      onHighlighted: setupOverlayClickAdvance
    })

    return steps
  }

  const getLayerSwitcherSteps = (options?: { skipOpenDrawer?: boolean }): DriveStep[] => {
    const steps: DriveStep[] = []
    const isMobile = appStore.isMobileOrTablet

    if (isMobile && !options?.skipOpenDrawer) {
      steps.push({
        element: TutorialSelector.DRAWER_TOGGLE,
        popover: {
          title: "Ouvrir le panneau de configuration",
          description:
            "Cliquez ici pour ouvrir le panneau de configuration et accéder aux options de calques.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: () => onClickAdvance(TutorialSelector.DRAWER_TOGGLE, "nextStep", "nextTick")
      })
    }

    steps.push({
      element: TutorialSelector.LAYER_SWITCHER,
      popover: {
        title: "Changement de calque",
        description:
          "Utilisez ce menu pour changer de calque et afficher différentes données sur la carte.",
        showButtons: NAV_BUTTONS
      },
      onHighlighted: setupOverlayClickAdvance
    })

    // Use different background selector based on device type
    const bgSelector = isMobile
      ? TutorialSelector.MAP_BG_SWITCHER
      : TutorialSelector.MAP_BACKGROUND_SELECTOR

    steps.push({
      element: bgSelector,
      popover: {
        title: "Fond de carte",
        description: "Vous pouvez également changer le fond de carte (satellite, plan, etc.).",
        showButtons: NAV_BUTTONS
      },
      onHighlighted: setupOverlayClickAdvance
    })

    return steps
  }

  const startMapTutorial = async () => {
    await ensureMapPage()
    runTutorial(getMapSteps())
  }

  const startLegendTutorial = async () => {
    await ensureMapPage()
    runTutorial([...getLegendSteps(), ...getLegendCloseSteps()])
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
      ...getLegendSteps({ skipOpenDrawer: isMobile }),
      ...getLayerSwitcherSteps({ skipOpenDrawer: isMobile })
    ]

    if (isMobile) {
      steps.push({
        element: TutorialSelector.DRAWER_CLOSE_BUTTON,
        popover: {
          title: "Fermer le panneau",
          description: "Cliquez sur la croix pour fermer le panneau.",
          showButtons: NAV_BUTTONS
        },
        onHighlighted: () =>
          onClickAdvance(TutorialSelector.DRAWER_CLOSE_BUTTON, "nextStep", "nextTick")
      })
    }

    steps.push(
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
    )

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
