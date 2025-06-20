import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"
import { DataType } from "@/utils/enum"
import { Layout } from "@/utils/constants"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView,
      meta: {
        layout: Layout.Map
      }
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability)/:zoom(\\d+)/:lat(\\d+.\\d+)/:lng(\\d+.\\d+)",
      name: "mapWithUrlParams",
      component: MapView,
      meta: {
        layout: Layout.Map
      }
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
