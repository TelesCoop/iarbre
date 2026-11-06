import type { HourlyRaster } from "@/utils/hourlyRaster"

export const SHADOW_RASTER: HourlyRaster = {
  endpoint: "shadow",
  axisLabels: ["Dense", "Légère"],
  columnLabels: ["Ombre", "Origine"],
  descriptionSummary: "En savoir plus sur l'ombre",
  classes: [
    {
      value: 0,
      color: "#00008b",
      label: "Ombre complète",
      detail: "Bâtiments principalement"
    },
    { value: 0.03, color: "#41ab5d", label: "Ombre des arbres", detail: "Feuillage des arbres" }
  ]
}
