import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability)/:zoom(\\d+)/:lat(\\d+.\\d+)/:lng(\\d+.\\d+)",
      name: "mapWithUrlParams",
      component: MapView
    }
  ]
})

export default router
