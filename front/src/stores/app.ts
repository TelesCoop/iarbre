import { Breakpoint, convertRemToPx } from "@/utils/breakpoints"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export enum Sidebar {
  MAP_SCORES = "map-scores",
  MAP_CONFIG = "map-config"
}
export const useAppStore = defineStore("app", () => {
  const windowWidth = ref(window.innerWidth)
  const sidebarVisible = ref({
    [Sidebar.MAP_SCORES]: false,
    [Sidebar.MAP_CONFIG]: false
  })

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

  const toggleSidebar = (sidebar: Sidebar) => {
    sidebarVisible.value[sidebar] = !sidebarVisible.value[sidebar]
  }

  const setSidebarVisible = (sidebar: Sidebar, visible: boolean) => {
    sidebarVisible.value[sidebar] = visible
  }

  return {
    windowWidth,
    sidebarVisible,
    isMobile,
    isMobileOrTablet,
    isDesktop,
    refreshWindowWidth,
    mountDetectResize,
    unmountDetectResize,
    toggleSidebar,
    setSidebarVisible
  }
})
