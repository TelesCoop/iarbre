import type { HourlyRaster } from "@/utils/hourlyRaster"

export const PET_YEARS = [2020, 2090] as const

export const DEFAULT_PET_YEAR = 2090

export const PET_RASTER: HourlyRaster = {
  endpoint: "pet",
  years: PET_YEARS,
  axisLabels: ["Frais", "Chaud"],
  columnLabels: ["Température ressentie", "Stress"],
  descriptionSummary: "En savoir plus sur le PET",
  classes: [
    {
      value: 4,
      color: "#9ecae1",
      label: "13 - 18 °C - Légèrement frais",
      detail: "Léger stress dû au froid"
    },
    { value: 5, color: "#ffffcc", label: "18 - 23 °C - Neutre", detail: "Aucun stress thermique" },
    {
      value: 6,
      color: "#fed976",
      label: "23 - 29 °C - Légèrement chaud",
      detail: "Léger stress thermique"
    },
    { value: 7, color: "#fd8d3c", label: "29 - 35 °C - Chaud", detail: "Stress thermique modéré" },
    {
      value: 8,
      color: "#e31a1c",
      label: "35 - 41 °C - Très chaud",
      detail: "Fort stress thermique"
    },
    {
      value: 9,
      color: "#800026",
      label: "> 41 °C - Extrêmement chaud",
      detail: "Stress thermique extrême"
    }
  ]
}
