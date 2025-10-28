import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"
import { DataType } from "@/utils/enum"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability|plantability_vulnerability|ipave)/:zoom(\\d+)/:lat(\\d+.\\d+)/:lng(\\d+.\\d+)",
      name: "mapWithUrlParams",
      component: MapView
    },
    {
      path: "/:zoom(\\d+)/:lat(\\d+\\.\\d+)/:lng(\\d+\\.\\d+)",
      redirect: (to) => {
        const { zoom, lat, lng } = to.params
        return {
          name: "mapWithUrlParams",
          params: {
            dataType: DataType.PLANTABILITY,
            zoom,
            lat,
            lng
          }
        }
      }
    }
  ]
})

export default router
