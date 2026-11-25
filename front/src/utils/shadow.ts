import type { HourlyRaster } from "@/utils/hourlyRaster"
import IconUmbrella from "@/components/icons/IconUmbrella.vue"

export const SHADOW_RASTER: HourlyRaster = {
  endpoint: "shadow",
  toggleLabel: "Ombre",
  icon: IconUmbrella,
  axisLabels: ["Dense", "Légère"],
  columnLabels: ["Ombre", "Origine"],
  descriptionSummary: "En savoir plus sur l'ombre",
  classes: [
    {
      value: 0,
      color: "#00008b",
      label: "Ombre complète",
      detail: "Bâtiments et reliefs"
    },
    { value: 0.03, color: "#41ab5d", label: "Ombre des arbres", detail: "Feuillage des arbres" }
  ]
}
