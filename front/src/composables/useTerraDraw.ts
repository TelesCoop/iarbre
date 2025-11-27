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

    // Initialize Terra Draw with all available modes
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

    // Limit to a single shape: remove previous shapes when a new one is created
    terraDraw.value.on("finish", () => {
      if (!terraDraw.value) return

      const features = terraDraw.value.getSnapshot()
      // If we have more than one shape, keep only the last one
      if (features.length > 1) {
        // Remove all shapes except the last one
        for (let i = 0; i < features.length - 1; i++) {
          const featureId = features[i].id
          if (featureId !== undefined) {
            terraDraw.value.removeFeatures([featureId])
          }
        }
      }

      // Automatically trigger calculation when a shape is finished
      if (onShapeFinishedCallback.value) {
        onShapeFinishedCallback.value()
      }
    })
  }

  const setMode = (mode: SelectionMode) => {
    if (!terraDraw.value) return

    // Clear existing shapes before changing mode
    terraDraw.value.clear()
    drawingPoints.value = []

    currentMode.value = mode

    // Map selection modes to Terra Draw modes
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

    // Get all drawn features
    const features = terraDraw.value.getSnapshot()
    if (features.length === 0) return null

    // For now, process the last drawn feature
    const lastFeature = features[features.length - 1]

    // Don't call API for LCZ in non-Point mode
    if (dataType === DataType.CLIMATE_ZONE || lastFeature.geometry.type === GeometryType.POINT) {
      return null
    }

    const coordinates: [number, number][] = (
      lastFeature.geometry.coordinates[0] as Array<[number, number]>
    ).map((coord) => [coord[0], coord[1]])

    if (coordinates.length < 3) return null

    // Call backend API to retrieve aggregated scores in polygon
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
