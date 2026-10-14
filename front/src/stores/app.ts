import { Breakpoint, convertRemToPx } from "@/utils/breakpoints"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useAppStore = defineStore("app", () => {
  const windowWidth = ref(window.innerWidth)
  const sidePanelVisible = ref(true)

  const isMobile = computed(() => windowWidth.value < convertRemToPx(Breakpoint.SM))
  const isMobileOrTablet = computed(() => windowWidth.value < convertRemToPx(Breakpoint.MD))
  const isDesktop = computed(() => windowWidth.value >= convertRemToPx(Breakpoint.MD))

  const refreshWindowWidth = () => {
    windowWidth.value = window.innerWidth
  }

  const mountDetectResize = () => {
    refreshWindowWidth() // Initial value
    window.addEventListener("resize", refreshWindowWidth)
  }

  const unmountDetectResize = () => {
    window.removeEventListener("resize", refreshWindowWidth)
  }

  const toggleSidePanel = () => {
    sidePanelVisible.value = !sidePanelVisible.value
  }

  return {
    windowWidth,
    sidePanelVisible,
    isMobile,
    isMobileOrTablet,
    isDesktop,
    refreshWindowWidth,
    mountDetectResize,
    unmountDetectResize,
    toggleSidePanel
  }
})
