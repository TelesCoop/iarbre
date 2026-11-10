import type { RasterLayer } from "@/utils/rasterLayers"

export const VECTOR_SOURCE_ID = "vector-source"

const PARK_RGB = "119, 123, 198"
const PARK_COLOR = `rgb(${PARK_RGB})`
const PARK_OPACITY = 0.75
const ISOCHRONE_OPACITY = 0.35
const PARK_EDGE_COLOR = "#3a3d8f"
const CASING_COLOR = "#ffffff"
const ISOCHRONE_DASH = [2, 1.5]

const BUILDING_COLORS = {
  none: "#c97a7a",
  some: "#eace7b",
  enough: "#63ab97"
}

const QUARTIER_COLORS = {
  low: "#ff6464",
  medium: "#fcb02f",
  high: "#3ee070"
}

export const LAYER_330300: RasterLayer = {
  key: "330300",
  label: "3-30-300",
  description: `<p>La règle 3-30-300 : voir au moins 3 arbres depuis chaque logement,
      30 % de couverture arborée dans chaque quartier et un parc à moins de 300 m.</p>`,
  attribution: "Métropole de Lyon, OpenStreetMap",
  hourly: false,
  legend: [],
  vectorSource: {
    tilesPath: "330300",
    maxzoom: 15,
    bounds: [4.69176, 45.55707, 5.062045, 45.939183]
  },
  styleLayers: [
    {
      id: "330300-isochrones",
      type: "fill",
      source: VECTOR_SOURCE_ID,
      "source-layer": "isochrones",
      paint: { "fill-color": PARK_COLOR, "fill-opacity": ISOCHRONE_OPACITY }
    },
    {
      id: "330300-isochrones-casing",
      type: "line",
      minzoom: 13,
      source: VECTOR_SOURCE_ID,
      "source-layer": "isochrones",
      paint: { "line-color": CASING_COLOR, "line-width": 4, "line-opacity": 0.8 }
    },
    {
      id: "330300-isochrones-outline",
      type: "line",
      minzoom: 13,
      source: VECTOR_SOURCE_ID,
      "source-layer": "isochrones",
      paint: { "line-color": PARK_EDGE_COLOR, "line-width": 2, "line-dasharray": ISOCHRONE_DASH }
    },
    {
      id: "330300-parks",
      type: "fill",
      source: VECTOR_SOURCE_ID,
      "source-layer": "parks",
      paint: { "fill-color": PARK_COLOR, "fill-opacity": PARK_OPACITY }
    },
    {
      id: "330300-parks-outline",
      type: "line",
      source: VECTOR_SOURCE_ID,
      "source-layer": "parks",
      paint: { "line-color": PARK_EDGE_COLOR, "line-width": 1.5 }
    },
    {
      id: "330300-buildings",
      type: "fill",
      source: VECTOR_SOURCE_ID,
      "source-layer": "buildings",
      minzoom: 14,
      paint: {
        "fill-color": [
          "match",
          ["get", "classe_arbres"],
          "Aucun arbre",
          BUILDING_COLORS.none,
          "Entre 1 et 2 arbres",
          BUILDING_COLORS.some,
          "3 arbres ou plus",
          BUILDING_COLORS.enough,
          BUILDING_COLORS.none
        ],
        "fill-outline-color": "#ffffff"
      }
    },
    {
      id: "330300-trees",
      type: "circle",
      source: VECTOR_SOURCE_ID,
      "source-layer": "trees",
      minzoom: 16,
      layout: { visibility: "none" },
      paint: { "circle-color": "#6fc055", "circle-radius": 1.5 }
    },
    {
      id: "330300-quartiers",
      type: "line",
      source: VECTOR_SOURCE_ID,
      "source-layer": "quartiers",
      paint: {
        "line-color": [
          "step",
          ["get", "pourcentage_arbo"],
          QUARTIER_COLORS.low,
          15,
          QUARTIER_COLORS.medium,
          30,
          QUARTIER_COLORS.high
        ],
        "line-width": ["interpolate", ["linear"], ["zoom"], 10, 1.5, 15, 4],
        "line-opacity": 0.662
      }
    }
  ],
  cards: [
    {
      key: "buildings",
      label: "3 - Arbres visibles",
      description: "Le 3 est visualisé par les bâtiments qui portent la valeur",
      legendStyle: "tile",
      legend: [
        { color: BUILDING_COLORS.none, label: "0", detail: "Arbre visible" },
        { color: BUILDING_COLORS.some, label: "1 à 2", detail: "Arbres visibles" },
        { color: BUILDING_COLORS.enough, label: "3+", detail: "Arbres visibles" }
      ],
      layerIds: ["330300-buildings"],
      subToggles: [
        {
          key: "trees",
          label: "Afficher les arbres",
          layerIds: ["330300-trees"],
          defaultHidden: true
        }
      ]
    },
    {
      key: "quartiers",
      label: "30 - Couverture arborée sur le quartier",
      description: "Le 30 est représenté par le contour du quartier",
      legendStyle: "outline",
      legend: [
        { color: QUARTIER_COLORS.low, label: "0 à 15 %", detail: "De canopée" },
        { color: QUARTIER_COLORS.medium, label: "15 à 30 %", detail: "De canopée" },
        { color: QUARTIER_COLORS.high, label: "+ 30 %", detail: "De canopée" }
      ],
      layerIds: ["330300-quartiers"]
    },
    {
      key: "parks",
      label: "300 - Accès aux parcs",
      description: "Le 300 est représenté par l’emprise des parcs",
      legendStyle: "swatch",
      legend: [
        { color: `rgba(${PARK_RGB}, ${PARK_OPACITY})`, label: "Emprise des parcs" },
        { color: `rgba(${PARK_RGB}, ${ISOCHRONE_OPACITY})`, label: "Zone d’influence des parcs" }
      ],
      layerIds: [
        "330300-parks",
        "330300-parks-outline",
        "330300-isochrones",
        "330300-isochrones-casing",
        "330300-isochrones-outline"
      ]
    }
  ]
}
