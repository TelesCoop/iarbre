import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"
import NotFoundView from "@/views/NotFoundView.vue"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability|plantability_vulnerability|vegetation)",
      redirect: (to) => {
        return {
          name: "mapWithUrlParams",
          params: {
            dataType: to.params.dataType,
            zoom: DEFAULT_MAP_PARAMS.zoom,
            lat: DEFAULT_MAP_PARAMS.lat.toFixed(5),
            lng: DEFAULT_MAP_PARAMS.lng.toFixed(5)
          }
        }
      }
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability|plantability_vulnerability|vegetation)/:zoom(\\d+)/:lat(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})/:lng(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})",
      redirect: (to) => {
        const { dataType, zoom, lat, lng } = to.params
        return {
          name: "mapWithUrlParams",
          params: {
            dataType,
            zoom,
            lat: parseFloat(lat as string).toFixed(5),
            lng: parseFloat(lng as string).toFixed(5)
          }
        }
      }
    },
    {
      path: "/:dataType(plantability|lcz|vulnerability|plantability_vulnerability|vegetation)/:zoom(\\d+)/:lat(-?\\d+\\.\\d{5})/:lng(-?\\d+\\.\\d{5})",
      name: "mapWithUrlParams",
      component: MapView
    },
    {
      path: "/:zoom(\\d+)/:lat(-?\\d+\\.\\d+)/:lng(-?\\d+\\.\\d+)",
      redirect: (to) => {
        const { zoom, lat, lng } = to.params
        return {
          name: "mapWithUrlParams",
          params: {
            dataType: DataType.PLANTABILITY,
            zoom,
            lat: parseFloat(lat as string).toFixed(5),
            lng: parseFloat(lng as string).toFixed(5)
          }
        }
      }
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue")
    },
    {
      path: "/mentions-legales",
      name: "legal",
      component: () => import("@/views/LegalView.vue")
    },
    {
      path: "/:pathMatch(.*)*",
      name: "notFound",
      component: NotFoundView
    }
  ]
})

export default router
