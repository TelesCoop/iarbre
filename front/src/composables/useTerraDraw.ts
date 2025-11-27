import { ref } from "vue"
import type { Map, LngLat } from "maplibre-gl"
import { getScoresInPolygon } from "@/services/tileService"
import { DataType, type SelectionMode } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import { GeometryType } from "@/types/map"
import { terraDrawStyles } from "@/utils/color"
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

    // Initialiser Terra Draw avec tous les modes disponibles
    terraDraw.value = new TerraDraw({
      adapter: new TerraDrawMapLibreGLAdapter({ map }),
      modes: [
        new TerraDrawPointMode({
          styles: {
            pointColor: terraDrawStyles.pointColor,
            pointWidth: terraDrawStyles.pointWidth,
            pointOutlineColor: terraDrawStyles.pointOutlineColor,
            pointOutlineWidth: terraDrawStyles.pointOutlineWidth
          }
        }),
        new TerraDrawPolygonMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth,
            closingPointColor: terraDrawStyles.pointColor,
            closingPointWidth: terraDrawStyles.pointWidth,
            closingPointOutlineColor: terraDrawStyles.pointOutlineColor,
            closingPointOutlineWidth: terraDrawStyles.pointOutlineWidth
          },
          pointerDistance: 40
        }),
        new TerraDrawRectangleMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawAngledRectangleMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawCircleMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawFreehandMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawSectorMode({
          styles: {
            fillColor: terraDrawStyles.fillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: terraDrawStyles.outlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawSelectMode({
          flags: {
            arbitrary: {
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

    // Ne pas appeler l'API pour LCZ en mode non-Point
    if (dataType === DataType.CLIMATE_ZONE && lastFeature.geometry.type !== GeometryType.POINT) {
      return null
    }

    let coordinates: [number, number][] = []

    // Extraire les coordonnées selon le type de géométrie
    if (lastFeature.geometry.type === GeometryType.POINT) {
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
    } else if (lastFeature.geometry.type === GeometryType.POLYGON) {
      coordinates = lastFeature.geometry.coordinates[0].map((coord: number[]) => [
        coord[0],
        coord[1]
      ])
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
    stopDrawing,
    clearDrawing,
    getScoresInShape,
    getSelectedFeatures,
    onShapeFinished,
    cleanup
  }
}
