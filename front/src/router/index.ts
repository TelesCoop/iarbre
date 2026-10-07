import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"
import NotFoundView from "@/views/NotFoundView.vue"
import { RASTER_LAYERS } from "@/utils/rasterLayers"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"

const layerBaseRegex = `/:layer(${RASTER_LAYERS.map((layer) => layer.key).join("|")})`

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView
    },
    {
      path: layerBaseRegex,
      redirect: (to) => {
        return {
          name: "mapWithUrlParams",
          params: {
            layer: to.params.layer,
            zoom: DEFAULT_MAP_PARAMS.zoom,
            lat: DEFAULT_MAP_PARAMS.lat.toFixed(5),
            lng: DEFAULT_MAP_PARAMS.lng.toFixed(5)
          }
        }
      }
    },
    {
      path: `${layerBaseRegex}/:zoom(\\d+)/:lat(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})/:lng(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})`,
      redirect: (to) => {
        const { layer, zoom, lat, lng } = to.params
        return {
          name: "mapWithUrlParams",
          params: {
            layer,
            zoom,
            lat: parseFloat(lat as string).toFixed(5),
            lng: parseFloat(lng as string).toFixed(5)
          }
        }
      }
    },
    {
      path: `${layerBaseRegex}/:zoom(\\d+)/:lat(-?\\d+\\.\\d{5})/:lng(-?\\d+\\.\\d{5})`,
      name: "mapWithUrlParams",
      component: MapView
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
