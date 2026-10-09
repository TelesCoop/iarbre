export interface LegendItem {
  color: string
  label: string
  detail?: string
}

export interface RasterLayer {
  key: string
  label: string
  description: string
  attribution: string
  hourly: boolean
  legend: LegendItem[]
}

export const RASTER_LAYERS: RasterLayer[] = [
  {
    key: "pet_index",
    label: "Indice PET - 1m - 2020",
    description: `<p>L'objectif ici est de simuler une journée typique (légèrement chaude) le 14 juillet 2020.
      Nous répliquons, avec son aide, une <a href="https://www.sciencedirect.com/science/article/pii/S0360132325007188" target="_blank" rel="noopener noreferrer">étude</a> menée par le chercheur Damien David du CETHIL.</p>
      <p>Le PET (Physiological Equivalent Temperature) est un indicateur reflétant le confort/inconfort
      d'une personne selon les caractéristiques d'ambiance (température de l'air, ombre ou soleil,
      vent, rayonnement secondaire des bâtiments et du sol). Ici, la personne est simulée assise et immobile.</p>
      <p>Les données d'entrée sont :</p>
      <ul>
        <li>Les bâtiments,</li>
        <li>Le modèle de hauteur de la végétation,</li>
        <li>L'occupation des sols (béton, terre, etc.),</li>
        <li>Projection météo 2020 heure par heure (température, humidité relative, vent).</li>
      </ul>
      <p>Les modélisations sont faites à l'aide du modèle open-source SOLWEIG.
      Chaque pixel correspond à une zone de 1mx1m.</p>`,
    attribution: "Métropole de Lyon",
    hourly: true,
    legend: [
      { color: "#ffffcc", label: "18 - 23 °C - Neutre", detail: "Aucun stress thermique" },
      {
        color: "#fed976",
        label: "23 - 29 °C - Légèrement chaud",
        detail: "Léger stress thermique"
      },
      { color: "#fd8d3c", label: "29 - 35 °C - Chaud", detail: "Stress thermique modéré" },
      { color: "#e31a1c", label: "35 - 41 °C - Très chaud", detail: "Fort stress thermique" },
      {
        color: "#800026",
        label: "> 41 °C - Extrêmement chaud",
        detail: "Stress thermique extrême"
      }
    ]
  }
]

export const DEFAULT_LAYER_KEY = RASTER_LAYERS[0].key

export const HOURS = Array.from({ length: 15 }, (_, index) => index + 7)

export const DEFAULT_HOUR = 16

export const getRasterLayer = (key: string): RasterLayer =>
  RASTER_LAYERS.find((layer) => layer.key === key) ?? RASTER_LAYERS[0]

export const formatHour = (hour: number): string => `${hour}h`

export const buildTileUrl = (
  baseApiUrl: string,
  layer: RasterLayer,
  hour: number,
  hiddenClasses: number[] = []
): string => {
  const params = new URLSearchParams({ mode: layer.key })
  if (layer.hourly) params.set("hour", String(hour))
  if (hiddenClasses.length) {
    const visibleClasses = layer.legend
      .map((_, index) => index)
      .filter((index) => !hiddenClasses.includes(index))
    params.set("classes", visibleClasses.join(","))
  }
  return `${baseApiUrl}/tiles/heat/{z}/{x}/{y}.png?${params}`
}

export const buildRasterUrl = (baseApiUrl: string, layer: RasterLayer, hour?: number): string => {
  const url = `${baseApiUrl}/rasters/${layer.key}/`
  return layer.hourly && hour !== undefined ? `${url}?hour=${hour}` : url
}
