import { createRouter, createWebHistory } from "vue-router"
import MapView from "@/views/MapView.vue"
import NotFoundView from "@/views/NotFoundView.vue"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"
import { useApiGet } from "@/api"
import { updatePageMeta } from "@/utils/seo"

const dataTypeBaseRegex = `/:dataType(${DataType.PLANTABILITY}|${DataType.VULNERABILITY}|${DataType.CLIMATE_ZONE}|${DataType.PLANTABILITY_VULNERABILITY}|${DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY}|${DataType.VEGESTRATE})`

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "map",
      component: MapView
    },
    {
      path: dataTypeBaseRegex,
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
      path: `${dataTypeBaseRegex}/:zoom(\\d+)/:lat(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})/:lng(-?\\d+\\.\\d{1,4}|\\d+\\.\\d{6,})`,
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
      path: `${dataTypeBaseRegex}/:zoom(\\d+)/:lat(-?\\d+\\.\\d{5})/:lng(-?\\d+\\.\\d{5})`,
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
      path: "/s/:code",
      component: { render: () => null },
      beforeEnter: async (to) => {
        const { data } = await useApiGet<{ path: string }>(`short-links/${to.params.code}/`)
        return data?.path ?? "/"
      }
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("@/views/DashboardView.vue"),
      meta: {
        title: "Tableau de bord",
        description:
          "Tableau de bord IA·rbre : statistiques de plantabilité, de chaleur et de végétation par commune et par IRIS de la Métropole de Lyon."
      }
    },
    {
      path: "/mentions-legales",
      name: "legal",
      component: () => import("@/views/LegalView.vue"),
      meta: {
        title: "Mentions légales",
        description: "Mentions légales et politique de confidentialité de la carte IA·rbre."
      }
    },
    {
      path: "/:pathMatch(.*)*",
      name: "notFound",
      component: NotFoundView,
      meta: { title: "Page introuvable", noindex: true }
    }
  ]
})

router.afterEach((to) => updatePageMeta(to))

export default router
