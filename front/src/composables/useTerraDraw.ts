import { ref } from "vue"
import type { Map, LngLat } from "maplibre-gl"
import { getScoresInPolygon } from "@/services/tileService"
import type { DataType, SelectionMode } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import {
  TerraDraw,
  TerraDrawPointMode,
  TerraDrawPolygonMode,
  TerraDrawRectangleMode,
  TerraDrawAngledRectangleMode,
  TerraDrawCircleMode,
  TerraDrawFreehandMode,
  TerraDrawSectorMode,
  TerraDrawSelectMode
} from "terra-draw"
import { TerraDrawMapLibreGLAdapter } from "terra-draw-maplibre-gl-adapter"

export function useShapeDrawing() {
  const isDrawing = ref(false)
  const drawingPoints = ref<LngLat[]>([])
  const currentMap = ref<Map | null>(null)
  const terraDraw = ref<TerraDraw | null>(null)
  const currentMode = ref<SelectionMode | null>(null)
  const onShapeFinishedCallback = ref<(() => void) | null>(null)

  const initDraw = (map: Map) => {
    currentMap.value = map

    // Styles communs pour tous les modes
    const commonStyles = {
      fillColor: "#92a48d" as `#${string}`,
      fillOpacity: 0.3,
      outlineColor: "#426A45" as `#${string}`,
      outlineWidth: 2,
      pointColor: "#426A45" as `#${string}`,
      pointWidth: 3,
      pointOutlineColor: "#ffffff" as `#${string}`,
      pointOutlineWidth: 2
    }

    // Initialiser Terra Draw avec tous les modes disponibles
    terraDraw.value = new TerraDraw({
      adapter: new TerraDrawMapLibreGLAdapter({ map }),
      modes: [
        new TerraDrawPointMode({
          styles: {
            pointColor: commonStyles.pointColor,
            pointWidth: commonStyles.pointWidth,
            pointOutlineColor: commonStyles.pointOutlineColor,
            pointOutlineWidth: commonStyles.pointOutlineWidth
          }
        }),
        new TerraDrawPolygonMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth,
            closingPointColor: commonStyles.pointColor,
            closingPointWidth: commonStyles.pointWidth,
            closingPointOutlineColor: commonStyles.pointOutlineColor,
            closingPointOutlineWidth: commonStyles.pointOutlineWidth
          },
          pointerDistance: 40
        }),
        new TerraDrawRectangleMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth
          }
        }),
        new TerraDrawAngledRectangleMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth
          }
        }),
        new TerraDrawCircleMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth
          }
        }),
        new TerraDrawFreehandMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth
          }
        }),
        new TerraDrawSectorMode({
          styles: {
            fillColor: commonStyles.fillColor,
            fillOpacity: commonStyles.fillOpacity,
            outlineColor: commonStyles.outlineColor,
            outlineWidth: commonStyles.outlineWidth
          }
        }),
        new TerraDrawSelectMode({
          flags: {
            arbitary: {
              feature: {}
            },
            polygon: {
              feature: {
                draggable: true
              }
            },
            point: {
              feature: {
                draggable: true
              }
            }
          }
        })
      ]
    })

    terraDraw.value.start()

    // Limiter à une seule forme : supprimer les formes précédentes quand une nouvelle est créée
    terraDraw.value.on("finish", () => {
      if (!terraDraw.value) return

      const features = terraDraw.value.getSnapshot()
      // Si on a plus d'une forme, garder seulement la dernière
      if (features.length > 1) {
        // Supprimer toutes les formes sauf la dernière
        for (let i = 0; i < features.length - 1; i++) {
          const featureId = features[i].id
          if (featureId !== undefined) {
            terraDraw.value.removeFeatures([featureId])
          }
        }
      }

      // Déclencher automatiquement le calcul quand une forme est terminée
      if (onShapeFinishedCallback.value) {
        onShapeFinishedCallback.value()
      }
    })
  }

  const setMode = (mode: SelectionMode) => {
    if (!terraDraw.value) return

    // Effacer les formes existantes avant de changer de mode
    terraDraw.value.clear()
    drawingPoints.value = []

    currentMode.value = mode

    // Mapper les modes de sélection aux modes Terra Draw
    const modeMap: Record<SelectionMode, string> = {
      point: "point",
      polygon: "polygon",
      rectangle: "rectangle",
      circle: "circle",
      "angled-rectangle": "angled-rectangle",
      sector: "sector",
      select: "select"
    }

    const terraDrawMode = modeMap[mode]
    terraDraw.value.setMode(terraDrawMode)
    isDrawing.value = terraDrawMode !== "select"
  }

  const startDrawing = () => {
    isDrawing.value = true
  }

  const addPoint = () => {
    // Cette méthode n'est plus nécessaire avec Terra Draw
    // Terra Draw gère les clics automatiquement
  }

  const stopDrawing = () => {
    if (terraDraw.value) {
      terraDraw.value.setMode("select")
    }
    isDrawing.value = false
  }

  const clearDrawing = () => {
    if (terraDraw.value) {
      terraDraw.value.clear()
    }
    drawingPoints.value = []
  }

  const getSelectedFeatures = () => {
    if (!terraDraw.value) return []
    return terraDraw.value.getSnapshot()
  }

  const getScoresInShape = async (
    dataType: DataType
  ): Promise<PlantabilityData | VulnerabilityData | ClimateData | null> => {
    if (!terraDraw.value) return null

    // Récupérer toutes les features dessinées
    const features = terraDraw.value.getSnapshot()
    if (features.length === 0) return null

    // Pour l'instant, on traite la dernière feature dessinée
    const lastFeature = features[features.length - 1]

    let coordinates: [number, number][] = []

    // Extraire les coordonnées selon le type de géométrie
    if (lastFeature.geometry.type === "Point") {
      // Pour un point, créer un petit polygone autour
      const [lng, lat] = lastFeature.geometry.coordinates
      const offset = 0.0001
      coordinates = [
        [lng - offset, lat - offset],
        [lng + offset, lat - offset],
        [lng + offset, lat + offset],
        [lng - offset, lat + offset],
        [lng - offset, lat - offset]
      ]
    } else if (lastFeature.geometry.type === "Polygon") {
      coordinates = lastFeature.geometry.coordinates[0].map((coord: number[]) => [
        coord[0],
        coord[1]
      ])
    } else if (lastFeature.geometry.type === "LineString") {
      // Pour les lignes (freehand), créer un polygone
      coordinates = lastFeature.geometry.coordinates.map((coord: number[]) => [coord[0], coord[1]])
      coordinates.push(coordinates[0]) // Fermer le polygone
    }

    if (coordinates.length < 3) return null

    // Appeler l'API backend pour récupérer les scores agrégés dans le polygone
    const scores = await getScoresInPolygon(coordinates, dataType)

    return scores
  }

  const cleanup = () => {
    if (terraDraw.value) {
      terraDraw.value.stop()
      terraDraw.value = null
    }
    currentMap.value = null
    drawingPoints.value = []
    isDrawing.value = false
    onShapeFinishedCallback.value = null
  }

  const onShapeFinished = (callback: () => void) => {
    onShapeFinishedCallback.value = callback
  }

  return {
    isDrawing,
    drawingPoints,
    currentMode,
    initDraw,
    setMode,
    startDrawing,
    addPoint,
    stopDrawing,
    clearDrawing,
    getScoresInShape,
    getSelectedFeatures,
    onShapeFinished,
    cleanup
  }
}
