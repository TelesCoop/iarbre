import { Breakpoint, convertRemToPx } from "@/utils/breakpoints"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useAppStore = defineStore("app", () => {
  const windowWidth = ref(window.innerWidth)
  const sidebarVisible = ref(false)

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

  const toggleSidebar = () => {
    sidebarVisible.value = !sidebarVisible.value
  }

  const setSidebarVisible = (visible: boolean) => {
    sidebarVisible.value = visible
  }

  return {
    windowWidth,
    sidebarVisible,
    isMobileOrTablet,
    isDesktop,
    refreshWindowWidth,
    mountDetectResize,
    unmountDetectResize,
    toggleSidebar,
    setSidebarVisible
  }
})
