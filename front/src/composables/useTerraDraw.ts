import { ref } from "vue"
import type { Map, LngLat } from "maplibre-gl"
import { getScoresInPolygon } from "@/services/tileService"
import { DataType, SelectionMode } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import { GeometryType } from "@/types/map"
import { terraDrawStyles } from "@/utils/color"
import { computePolygonAreaM2 } from "@/utils/geo"
import { MAX_SHAPE_AREA_M2 } from "@/utils/constants"
import {
  TerraDraw,
  TerraDrawPointMode,
  TerraDrawPolygonMode,
  TerraDrawRectangleMode,
  TerraDrawAngledRectangleMode,
  TerraDrawCircleMode,
  TerraDrawSelectMode
} from "terra-draw"
import { TerraDrawMapLibreGLAdapter } from "terra-draw-maplibre-gl-adapter"

// Structural feature shape — terra-draw's GeoJSONStoreFeatures is not re-exported.
type StyledFeature = { geometry: { type: string; coordinates: unknown } }

const isOverAreaLimit = (feature: StyledFeature): boolean =>
  feature.geometry.type === GeometryType.POLYGON &&
  computePolygonAreaM2((feature.geometry.coordinates as number[][][])[0]) > MAX_SHAPE_AREA_M2

// Live size feedback: a too-large area is drawn in red while tracing and editing.
const areaOutlineColor = (feature: StyledFeature): `#${string}` =>
  isOverAreaLimit(feature) ? terraDrawStyles.errorColor : terraDrawStyles.outlineColor

const areaFillColor = (feature: StyledFeature): `#${string}` =>
  isOverAreaLimit(feature) ? terraDrawStyles.errorColor : terraDrawStyles.fillColor

// Lets the user draw/extend a zone beyond the limit, but blocks only its
// finalization — an oversized selection can be traced (in red) yet never completed.
const validateAreaLimit = (feature: StyledFeature, context: { updateType: string }) =>
  context.updateType === "finish" && isOverAreaLimit(feature)
    ? { valid: false, reason: "Zone trop grande" }
    : { valid: true }

// Polygons, rectangles and angled rectangles get editable vertices; a circle does
// not (dragging its approximation points distorts it), so it is only draggable as a
// whole. Select-mode flags are keyed by the CREATING mode's name, so every shape
// mode needs its own entry — otherwise its features are not editable at all.
const POLYGON_EDIT_FLAGS = {
  feature: {
    draggable: true,
    coordinates: {
      midpoints: { draggable: true },
      draggable: true,
      deletable: true
    }
  }
}
// A circle stays round and is only moved as a whole — no resize handles (those would
// be one per segment, cluttering the smooth shape).
const WHOLE_SHAPE_FLAGS = { feature: { draggable: true } }

const SELECT_FLAGS = {
  arbitrary: WHOLE_SHAPE_FLAGS,
  polygon: POLYGON_EDIT_FLAGS,
  rectangle: POLYGON_EDIT_FLAGS,
  "angled-rectangle": POLYGON_EDIT_FLAGS,
  circle: WHOLE_SHAPE_FLAGS,
  point: WHOLE_SHAPE_FLAGS
}

export function useShapeDrawing() {
  const isDrawing = ref(false)
  const drawingPoints = ref<LngLat[]>([])
  const currentMap = ref<Map | null>(null)
  const terraDraw = ref<TerraDraw | null>(null)
  const currentMode = ref<SelectionMode | null>(null)
  const onShapeFinishedCallback = ref<(() => void) | null>(null)
  const onShapeChangedCallback = ref<(() => void) | null>(null)

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
          validation: validateAreaLimit,
          styles: {
            fillColor: areaFillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: areaOutlineColor,
            outlineWidth: terraDrawStyles.outlineWidth,
            closingPointColor: terraDrawStyles.pointColor,
            closingPointWidth: terraDrawStyles.pointWidth,
            closingPointOutlineColor: terraDrawStyles.pointOutlineColor,
            closingPointOutlineWidth: terraDrawStyles.pointOutlineWidth
          },
          pointerDistance: 40
        }),
        new TerraDrawRectangleMode({
          validation: validateAreaLimit,
          styles: {
            fillColor: areaFillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: areaOutlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawAngledRectangleMode({
          validation: validateAreaLimit,
          styles: {
            fillColor: areaFillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: areaOutlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawCircleMode({
          validation: validateAreaLimit,
          // Smooth circle; vertex count stays well under the backend's limit
          // (ScoresInPolygonView.MAX_VERTICES).
          segments: 64,
          styles: {
            fillColor: areaFillColor,
            fillOpacity: terraDrawStyles.fillOpacity,
            outlineColor: areaOutlineColor,
            outlineWidth: terraDrawStyles.outlineWidth
          }
        }),
        new TerraDrawSelectMode({
          validation: validateAreaLimit,
          flags: SELECT_FLAGS,
          styles: {
            selectedPolygonColor: areaFillColor,
            selectedPolygonFillOpacity: terraDrawStyles.fillOpacity,
            selectedPolygonOutlineColor: areaOutlineColor,
            selectedPolygonOutlineWidth: terraDrawStyles.outlineWidth
          }
        })
      ]
    })

    terraDraw.value.start()

    // FeatureId = string | number in terra-draw (not re-exported from package root)
    // When a shape is finished, switch to select mode so its vertices become editable.
    terraDraw.value.on("finish", (id: string | number) => {
      // Keep the finished shape and make it editable: switch to select WITHOUT
      // clearing. Per-mode SELECT_FLAGS already grant the right editability
      // (vertex editing for polygon/rectangle/angled, whole-shape move for circle).
      if (terraDraw.value) {
        terraDraw.value.setMode("select")
        terraDraw.value.selectFeature(id)
      }

      isDrawing.value = false

      if (onShapeFinishedCallback.value) onShapeFinishedCallback.value()
    })

    // Select mode adds its own helper features (midpoints, selection points), so we
    // never reconcile features here — switching shape/mode always clears via setMode.
    terraDraw.value.on("change", (_ids: (string | number)[], type: string) => {
      // Skip cosmetic selection/deselection events to avoid triggering API calls
      if (type !== "styling" && onShapeChangedCallback.value) onShapeChangedCallback.value()
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
      select: "select"
    }

    const terraDrawMode = modeMap[mode]
    terraDraw.value.setMode(terraDrawMode)
    isDrawing.value = terraDrawMode !== "select"
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

    // Don't call API for LCZ in non-Point mode
    if (dataType === DataType.CLIMATE_ZONE) return null

    // Pick the drawn polygon explicitly; select mode also injects helper Point features.
    const polygon = terraDraw.value
      .getSnapshot()
      .find((f) => f.geometry.type === GeometryType.POLYGON)
    if (!polygon) return null

    const coordinates: [number, number][] = (
      polygon.geometry.coordinates[0] as Array<[number, number]>
    ).map((coord) => [coord[0], coord[1]])

    if (coordinates.length < 3) return null

    // Call backend API to retrieve aggregated scores in polygon
    const scores = await getScoresInPolygon(coordinates, dataType)

    return scores
  }

  const onShapeChanged = (callback: () => void) => {
    onShapeChangedCallback.value = callback
  }

  /** Coordinates ring of the drawn polygon feature, or null when none is present. */
  const getCurrentShapeCoordinates = (): number[][] | null => {
    if (!terraDraw.value) return null
    const polygon = terraDraw.value
      .getSnapshot()
      .find((f) => f.geometry.type === GeometryType.POLYGON)
    if (!polygon) return null
    return polygon.geometry.coordinates[0] as number[][]
  }

  /**
   * Programmatically finish an in-progress polygon by dispatching the configured
   * finish key (Enter). The event must target the canvas itself — TerraDraw's
   * MapLibre adapter registers its keyup listener on map.getCanvas(), and keyup
   * bubbles upward, so dispatching on the parent container would never reach it.
   */
  const finishCurrentPolygon = () => {
    if (!currentMap.value || currentMode.value !== SelectionMode.POLYGON) return
    const canvas = currentMap.value.getCanvas()
    canvas.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", bubbles: true }))
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
    onShapeChangedCallback.value = null
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
    stopDrawing,
    clearDrawing,
    getScoresInShape,
    getSelectedFeatures,
    onShapeFinished,
    onShapeChanged,
    getCurrentShapeCoordinates,
    finishCurrentPolygon,
    cleanup
  }
}
