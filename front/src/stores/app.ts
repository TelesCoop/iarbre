import { Breakpoint, convertRemToPx } from "@/utils/breakpoints"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export enum Drawer {
  MAP_SCORES = "map-scores",
  MAP_CONFIG = "map-config"
}
export const useAppStore = defineStore("app", () => {
  const windowWidth = ref(window.innerWidth)
  const drawerVisible = ref({
    [Drawer.MAP_SCORES]: false,
    [Drawer.MAP_CONFIG]: false
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

  const toggleDrawer = (drawer: Drawer) => {
    drawerVisible.value[drawer] = !drawerVisible.value[drawer]
  }

  const setDrawerVisible = (drawer: Drawer, visible: boolean) => {
    drawerVisible.value[drawer] = visible
  }

  return {
    windowWidth,
    drawerVisible,
    isMobile,
    isMobileOrTablet,
    isDesktop,
    refreshWindowWidth,
    mountDetectResize,
    unmountDetectResize,
    toggleDrawer,
    setDrawerVisible
  }
})
