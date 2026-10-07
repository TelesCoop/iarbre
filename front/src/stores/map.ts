import { markRaw, ref } from "vue"
import { defineStore } from "pinia"
import {
  Map,
  NavigationControl,
  type RasterTileSource,
  type StyleSpecification,
  type DataDrivenPropertyValueSpecification
} from "maplibre-gl"
import { MAP_CONTROL_POSITION, MAX_ZOOM, MIN_ZOOM, DEFAULT_MAP_CENTER } from "@/utils/constants"
import { MapStyle } from "@/utils/enum"
import mapStyles from "@/map/map-style.json"
import { applyMapStyleAttributions } from "@/utils/mapStyleOptions"
import { getFullBaseApiUrl } from "@/api"
import { getQPVData } from "@/services/qpvService"
import { getCityBoundaries } from "@/services/boundaryService"
import {
  DEFAULT_HOUR,
  DEFAULT_LAYER_KEY,
  buildTileUrl,
  getRasterLayer,
  type RasterLayer
} from "@/utils/rasterLayers"
import {
  QPV_CASING_COLOR,
  QPV_CASING_WIDTH,
  QPV_CASING_OPACITY,
  QPV_BORDER_COLOR,
  QPV_BORDER_WIDTH,
  QPV_BORDER_OPACITY,
  CITY_BORDER_COLOR,
  CITY_BORDER_WIDTH,
  CITY_BORDER_OPACITY,
  CADASTRE_COLOR,
  CADASTRE_BORDER_WIDTH,
  CADASTRE_BORDER_OPACITY,
  CADASTRE_SELECTED_BORDER_WIDTH,
  CADASTRE_SELECTED_BORDER_OPACITY,
  CADASTRE_SELECTED_FILL_OPACITY,
  CADASTRE_DEFAULT_FILL_OPACITY,
  CITY_CASING_COLOR,
  CITY_CASING_WIDTH,
  CITY_CASING_OPACITY,
  PANORAMAX_SEQUENCE_COLOR,
  PANORAMAX_SEQUENCE_OPACITY,
  PANORAMAX_PICTURE_360_COLOR,
  PANORAMAX_PICTURE_FLAT_COLOR,
  PANORAMAX_PICTURE_STROKE_COLOR,
  PANORAMAX_PICTURE_STROKE_WIDTH,
  PANORAMAX_PICTURE_OPACITY,
  PANORAMAX_SELECTED_PICTURE_COLOR,
  PANORAMAX_SELECTED_PICTURE_STROKE_WIDTH
} from "@/utils/mapLayers"
import { getPicture, type PanoramaxPicture } from "maplibre-gl-panoramax"
import {
  PANORAMAX_API,
  PANORAMAX_SOURCE_ID,
  PANORAMAX_SEQUENCES_LAYER,
  PANORAMAX_PICTURES_LAYER,
  PANORAMAX_SOURCE_MAX_ZOOM,
  PANORAMAX_SEQUENCES_MIN_ZOOM,
  PANORAMAX_PICTURES_MIN_ZOOM,
  PANORAMAX_ACTIVATION_ZOOM
} from "@/utils/panoramax"
import { addCenterControl } from "@/utils/mapControls"

const RASTER_SOURCE_ID = "raster-source"
const RASTER_LAYER_ID = "raster-layer"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const selectedLayer = ref<RasterLayer>(getRasterLayer(DEFAULT_LAYER_KEY))
  const selectedHour = ref<number>(DEFAULT_HOUR)
  const hiddenClasses = ref<number[]>([])
  const selectedMapStyle = ref<MapStyle>(MapStyle.ORTHOPHOTO)
  const currentZoom = ref<number>(14)
  const showQPVLayer = ref<boolean>(false)
  const showBoundaryLayer = ref<boolean>(false)
  const showCadastreLayer = ref<boolean>(false)
  const selectedCadastreParcel = ref<{
    parcelId: string
    section: string
    numero: string
    surface: number | null
  } | null>(null)
  const showPanoramaxLayer = ref<boolean>(false)
  const selectedPanoramaxPicture = ref<PanoramaxPicture | null>(null)
  const clickCoordinates = ref<{ lat: number; lng: number }>({
    lat: DEFAULT_MAP_CENTER.lat,
    lng: DEFAULT_MAP_CENTER.lng
  })

  /**
   * Deep-clone the raw maplibre style JSON for a given MapStyle, inject the
   * backend base URL and the Carto basemap key where needed and apply
   * centralized source attributions. When no Carto key is configured, the
   * `?key=` parameter is dropped so the keyless basemaps are used.
   * Reference: https://maplibre.org/maplibre-gl-js/docs/examples/map-tiles/
   * https://www.reddit.com/r/QGIS/comments/q0su5b/comment/hfabj8f/
   */
  const loadMapStyle = (style: MapStyle): StyleSpecification => {
    const cartoApiKey = import.meta.env.VITE_CARTO_API_KEY
    const rawStyle = JSON.stringify(mapStyles[style])
      .replace("{API_BASE_URL}", getFullBaseApiUrl())
      .replace(/\?key=\{CARTO_API_KEY\}/g, cartoApiKey ? `?key=${cartoApiKey}` : "")
    return applyMapStyleAttributions(JSON.parse(rawStyle)) as StyleSpecification
  }

  const getMapInstance = (mapId: string): Map => {
    return mapInstancesByIds.value[mapId]
  }

  const getMapId = (map: Map): string => {
    return Object.keys(mapInstancesByIds.value).find((key) => mapInstancesByIds.value[key] === map)!
  }

  const getTileUrl = () =>
    buildTileUrl(getFullBaseApiUrl(), selectedLayer.value, selectedHour.value, hiddenClasses.value)

  const addRasterLayer = (mapInstance: Map) => {
    if (!mapInstance.getSource(RASTER_SOURCE_ID)) {
      mapInstance.addSource(RASTER_SOURCE_ID, {
        type: "raster",
        tiles: [getTileUrl()],
        tileSize: 256,
        minzoom: MIN_ZOOM
      })
    }
    if (!mapInstance.getLayer(RASTER_LAYER_ID)) {
      mapInstance.addLayer({
        id: RASTER_LAYER_ID,
        type: "raster",
        source: RASTER_SOURCE_ID,
        paint: { "raster-opacity": 0.6 }
      })
    }
  }

  const updateRasterTiles = () => {
    const tileUrl = getTileUrl()
    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      mapInstance.getSource<RasterTileSource>(RASTER_SOURCE_ID)?.setTiles([tileUrl])
    })
  }

  const setLayer = (key: string) => {
    selectedLayer.value = getRasterLayer(key)
    hiddenClasses.value = []
    updateRasterTiles()
  }

  const toggleClass = (index: number) => {
    hiddenClasses.value = hiddenClasses.value.includes(index)
      ? hiddenClasses.value.filter((hidden) => hidden !== index)
      : [...hiddenClasses.value, index]
    updateRasterTiles()
  }

  const setHour = (hour: number) => {
    selectedHour.value = hour
    updateRasterTiles()
  }

  const addOverlays = (mapInstance: Map) => {
    if (showQPVLayer.value) addQPVLayer(mapInstance)
    if (showBoundaryLayer.value) addBoundaryLayers(mapInstance)
    if (showCadastreLayer.value) addCadastreLayer(mapInstance)
    if (showPanoramaxLayer.value) addPanoramaxLayer(mapInstance)
  }

  const removeOverlays = (mapInstance: Map) => {
    if (mapInstance.getLayer("qpv-border")) removeQPVLayer(mapInstance)
    if (mapInstance.getLayer("city-boundary")) removeBoundaryLayers(mapInstance)
    if (mapInstance.getLayer("cadastre-fill")) removeCadastreLayer(mapInstance)
    if (mapInstance.getLayer(PANORAMAX_PICTURES_LAYER)) removePanoramaxLayer(mapInstance)
  }

  const changeMapStyle = (mapstyle: MapStyle) => {
    selectedMapStyle.value = mapstyle
    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      removeOverlays(mapInstance)
      mapInstance.setStyle(loadMapStyle(mapstyle))
      addRasterLayer(mapInstance)
      addOverlays(mapInstance)
      mapInstance.fire("moveend")
    })
  }

  // TODO: display loading during the async execution
  const addQPVLayer = async (mapInstance: Map) => {
    if (!mapInstance.getSource("qpv-source")) {
      const data = await getQPVData()
      if (!data) {
        return
      }

      mapInstance.addSource("qpv-source", {
        type: "geojson",
        data: data
      })
    }

    if (!mapInstance.getLayer("qpv-border")) {
      // White casing drawn first so the coloured line stays legible on any basemap
      mapInstance.addLayer({
        id: "qpv-border-casing",
        type: "line",
        source: "qpv-source",
        paint: {
          "line-color": QPV_CASING_COLOR,
          "line-width": QPV_CASING_WIDTH,
          "line-opacity": QPV_CASING_OPACITY
        }
      })

      // Main QPV border drawn on top of the casing
      mapInstance.addLayer({
        id: "qpv-border",
        type: "line",
        source: "qpv-source",
        paint: {
          "line-color": QPV_BORDER_COLOR,
          "line-width": QPV_BORDER_WIDTH,
          "line-opacity": QPV_BORDER_OPACITY
        }
      })
    }
    mapInstance.once("render", () => {
      console.info(`cypress: QPV data loaded`)
    })
  }

  const removeQPVLayer = (mapInstance: Map) => {
    if (mapInstance.getLayer("qpv-border")) {
      mapInstance.removeLayer("qpv-border")
    }
    if (mapInstance.getLayer("qpv-border-casing")) {
      mapInstance.removeLayer("qpv-border-casing")
      mapInstance.once("render", () => {
        console.info(`cypress: QPV data removed`)
      })
    }
    if (mapInstance.getSource("qpv-source")) {
      mapInstance.removeSource("qpv-source")
    }
  }

  const toggleQPVLayer = async () => {
    showQPVLayer.value = !showQPVLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showQPVLayer.value) {
        await addQPVLayer(mapInstance)
      } else {
        removeQPVLayer(mapInstance)
      }
    }
  }

  const addBoundaryLayers = async (mapInstance: Map) => {
    if (!mapInstance.getSource("city-boundary-source")) {
      const cityData = await getCityBoundaries()
      if (!cityData) return

      mapInstance.addSource("city-boundary-source", {
        type: "geojson",
        data: cityData
      })
    }

    if (!mapInstance.getLayer("city-boundary")) {
      // White casing drawn first so the coloured line stays legible on any basemap
      mapInstance.addLayer({
        id: "city-boundary-border-casing",
        type: "line",
        source: "city-boundary-source",
        paint: {
          "line-color": CITY_CASING_COLOR,
          "line-width": CITY_CASING_WIDTH,
          "line-opacity": CITY_CASING_OPACITY
        }
      })
      mapInstance.addLayer({
        id: "city-boundary",
        type: "line",
        source: "city-boundary-source",
        paint: {
          "line-color": CITY_BORDER_COLOR,
          "line-width": CITY_BORDER_WIDTH,
          "line-opacity": CITY_BORDER_OPACITY
        }
      })
    }
  }

  const removeBoundaryLayers = (mapInstance: Map) => {
    if (mapInstance.getLayer("city-boundary")) {
      mapInstance.removeLayer("city-boundary")
    }
    if (mapInstance.getLayer("city-boundary-border-casing")) {
      mapInstance.removeLayer("city-boundary-border-casing")
    }
    if (mapInstance.getSource("city-boundary-source")) {
      mapInstance.removeSource("city-boundary-source")
    }
  }

  const toggleBoundaryLayer = async () => {
    showBoundaryLayer.value = !showBoundaryLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showBoundaryLayer.value) {
        await addBoundaryLayers(mapInstance)
      } else {
        removeBoundaryLayers(mapInstance)
      }
    }
  }

  type LayerInteractions = Record<string, (e: any) => void>

  const layerInteractions = ref<Record<string, LayerInteractions>>({})

  const interactionKey = (mapInstance: Map, layerId: string) =>
    `${getMapId(mapInstance)}:${layerId}`

  const unregisterLayerInteractions = (mapInstance: Map, layerId: string) => {
    const key = interactionKey(mapInstance, layerId)
    const handlers = layerInteractions.value[key]
    if (!handlers) return

    for (const [eventType, handler] of Object.entries(handlers)) {
      mapInstance.off(eventType as any, layerId, handler)
    }
    delete layerInteractions.value[key]
  }

  const registerLayerInteractions = (
    mapInstance: Map,
    layerId: string,
    handlers: LayerInteractions
  ) => {
    unregisterLayerInteractions(mapInstance, layerId)

    for (const [eventType, handler] of Object.entries(handlers)) {
      mapInstance.on(eventType as any, layerId, handler)
    }
    layerInteractions.value[interactionKey(mapInstance, layerId)] = handlers
  }

  const addCadastreLayer = (mapInstance: Map) => {
    const fullBaseApiUrl = getFullBaseApiUrl()

    if (!mapInstance.getSource("cadastre-source")) {
      mapInstance.addSource("cadastre-source", {
        type: "vector",
        tiles: [`${fullBaseApiUrl}/tiles/cadastre/cadastre/{z}/{x}/{y}.mvt`],
        minzoom: MIN_ZOOM,
        maxzoom: MAX_ZOOM - 1
      })
    }

    if (!mapInstance.getLayer("cadastre-fill")) {
      mapInstance.addLayer({
        id: "cadastre-fill",
        type: "fill",
        source: "cadastre-source",
        "source-layer": "cadastre--cadastre",
        paint: {
          "fill-color": CADASTRE_COLOR,
          "fill-opacity": 0.0
        }
      })
    }

    if (!mapInstance.getLayer("cadastre-border")) {
      mapInstance.addLayer({
        id: "cadastre-border",
        type: "line",
        source: "cadastre-source",
        "source-layer": "cadastre--cadastre",
        paint: {
          "line-color": CADASTRE_COLOR,
          "line-width": CADASTRE_BORDER_WIDTH,
          "line-opacity": CADASTRE_BORDER_OPACITY
        }
      })
    }

    const clickHandler = (e: any) => {
      if (!e.features || e.features.length === 0) return

      const featureProps = e.features[0].properties
      const parcelId = featureProps.parcel_id

      selectedCadastreParcel.value = {
        parcelId: parcelId ?? "",
        section: featureProps.section ?? "",
        numero: featureProps.numero ?? "",
        surface: featureProps.surface ?? null
      }

      mapInstance.setPaintProperty("cadastre-fill", "fill-opacity", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_FILL_OPACITY,
        CADASTRE_DEFAULT_FILL_OPACITY
      ])
      mapInstance.setPaintProperty("cadastre-border", "line-width", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_BORDER_WIDTH,
        CADASTRE_BORDER_WIDTH
      ])
      mapInstance.setPaintProperty("cadastre-border", "line-opacity", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_BORDER_OPACITY,
        CADASTRE_BORDER_OPACITY
      ])
    }

    const mouseEnterHandler = () => {
      mapInstance.getCanvas().style.cursor = "pointer"
    }
    const mouseLeaveHandler = () => {
      mapInstance.getCanvas().style.cursor = ""
    }

    registerLayerInteractions(mapInstance, "cadastre-fill", {
      click: clickHandler,
      mouseenter: mouseEnterHandler,
      mouseleave: mouseLeaveHandler
    })

    mapInstance.once("render", () => {
      console.info("cypress: cadastre data loaded")
    })
  }

  const clearCadastreSelection = () => {
    if (!selectedCadastreParcel.value) return
    selectedCadastreParcel.value = null

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]
      if (!mapInstance.getLayer("cadastre-fill")) continue
      mapInstance.setPaintProperty("cadastre-fill", "fill-opacity", CADASTRE_DEFAULT_FILL_OPACITY)
      mapInstance.setPaintProperty("cadastre-border", "line-width", CADASTRE_BORDER_WIDTH)
      mapInstance.setPaintProperty("cadastre-border", "line-opacity", CADASTRE_BORDER_OPACITY)
    }
  }

  const removeCadastreLayer = (mapInstance: Map) => {
    selectedCadastreParcel.value = null

    unregisterLayerInteractions(mapInstance, "cadastre-fill")

    if (mapInstance.getLayer("cadastre-fill")) {
      mapInstance.removeLayer("cadastre-fill")
    }
    if (mapInstance.getLayer("cadastre-border")) {
      mapInstance.removeLayer("cadastre-border")
    }
    if (mapInstance.getSource("cadastre-source")) {
      mapInstance.removeSource("cadastre-source")
    }

    mapInstance.once("render", () => {
      console.info("cypress: cadastre data removed")
    })
  }

  const toggleCadastreLayer = () => {
    showCadastreLayer.value = !showCadastreLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showCadastreLayer.value) {
        addCadastreLayer(mapInstance)
      } else {
        removeCadastreLayer(mapInstance)
      }
    }
  }

  let pendingPanoramaxPictureId: string | null = null

  const highlightPanoramaxPicture = (mapInstance: Map, pictureId: string | null) => {
    if (!mapInstance.getLayer(PANORAMAX_PICTURES_LAYER)) return

    const baseColor: DataDrivenPropertyValueSpecification<string> = [
      "case",
      ["==", ["get", "type"], "equirectangular"],
      PANORAMAX_PICTURE_360_COLOR,
      PANORAMAX_PICTURE_FLAT_COLOR
    ]

    mapInstance.setPaintProperty(
      PANORAMAX_PICTURES_LAYER,
      "circle-color",
      pictureId
        ? ([
            "match",
            ["get", "id"],
            pictureId,
            PANORAMAX_SELECTED_PICTURE_COLOR,
            baseColor
          ] as DataDrivenPropertyValueSpecification<string>)
        : baseColor
    )
    mapInstance.setPaintProperty(
      PANORAMAX_PICTURES_LAYER,
      "circle-stroke-width",
      pictureId
        ? ([
            "match",
            ["get", "id"],
            pictureId,
            PANORAMAX_SELECTED_PICTURE_STROKE_WIDTH,
            PANORAMAX_PICTURE_STROKE_WIDTH
          ] as DataDrivenPropertyValueSpecification<number>)
        : PANORAMAX_PICTURE_STROKE_WIDTH
    )
  }

  const addPanoramaxLayer = (mapInstance: Map) => {
    if (!mapInstance.getSource(PANORAMAX_SOURCE_ID)) {
      mapInstance.addSource(PANORAMAX_SOURCE_ID, {
        type: "vector",
        tiles: [`${PANORAMAX_API}/map/{z}/{x}/{y}.mvt`],
        minzoom: PANORAMAX_SEQUENCES_MIN_ZOOM,
        maxzoom: PANORAMAX_SOURCE_MAX_ZOOM
      })
    }

    if (!mapInstance.getLayer(PANORAMAX_SEQUENCES_LAYER)) {
      mapInstance.addLayer({
        id: PANORAMAX_SEQUENCES_LAYER,
        type: "line",
        source: PANORAMAX_SOURCE_ID,
        "source-layer": "sequences",
        minzoom: PANORAMAX_SEQUENCES_MIN_ZOOM,
        paint: {
          "line-color": PANORAMAX_SEQUENCE_COLOR,
          "line-width": ["interpolate", ["linear"], ["zoom"], 13, 1, 16, 3],
          "line-opacity": PANORAMAX_SEQUENCE_OPACITY
        }
      })
    }

    if (!mapInstance.getLayer(PANORAMAX_PICTURES_LAYER)) {
      mapInstance.addLayer({
        id: PANORAMAX_PICTURES_LAYER,
        type: "circle",
        source: PANORAMAX_SOURCE_ID,
        "source-layer": "pictures",
        minzoom: PANORAMAX_PICTURES_MIN_ZOOM,
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 17, 4, 22, 8],
          "circle-color": [
            "case",
            ["==", ["get", "type"], "equirectangular"],
            PANORAMAX_PICTURE_360_COLOR,
            PANORAMAX_PICTURE_FLAT_COLOR
          ],
          "circle-stroke-color": PANORAMAX_PICTURE_STROKE_COLOR,
          "circle-stroke-width": PANORAMAX_PICTURE_STROKE_WIDTH,
          "circle-opacity": PANORAMAX_PICTURE_OPACITY
        }
      })
    }

    highlightPanoramaxPicture(mapInstance, selectedPanoramaxPicture.value?.id ?? null)

    const clickHandler = async (e: any) => {
      if (!e.features || e.features.length === 0) return

      const pictureId = e.features[0].properties.id
      if (!pictureId) return

      pendingPanoramaxPictureId = pictureId
      highlightPanoramaxPicture(mapInstance, pictureId)

      try {
        const picture = await getPicture(pictureId, PANORAMAX_API)
        if (pendingPanoramaxPictureId !== pictureId) return
        selectedPanoramaxPicture.value = picture
      } catch (error) {
        if (pendingPanoramaxPictureId !== pictureId) return
        console.error("Panoramax: could not load picture", pictureId, error)
        selectedPanoramaxPicture.value = null
        highlightPanoramaxPicture(mapInstance, null)
      }
    }

    const mouseEnterHandler = () => {
      mapInstance.getCanvas().style.cursor = "pointer"
    }
    const mouseLeaveHandler = () => {
      mapInstance.getCanvas().style.cursor = ""
    }

    registerLayerInteractions(mapInstance, PANORAMAX_PICTURES_LAYER, {
      click: clickHandler,
      mouseenter: mouseEnterHandler,
      mouseleave: mouseLeaveHandler
    })

    mapInstance.once("render", () => {
      console.info("cypress: panoramax data loaded")
    })
  }

  const clearPanoramaxSelection = () => {
    pendingPanoramaxPictureId = null
    selectedPanoramaxPicture.value = null

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      highlightPanoramaxPicture(mapInstancesByIds.value[mapId], null)
    }
  }

  const removePanoramaxLayer = (mapInstance: Map) => {
    unregisterLayerInteractions(mapInstance, PANORAMAX_PICTURES_LAYER)

    mapInstance.getCanvas().style.cursor = ""

    if (mapInstance.getLayer(PANORAMAX_PICTURES_LAYER)) {
      mapInstance.removeLayer(PANORAMAX_PICTURES_LAYER)
    }
    if (mapInstance.getLayer(PANORAMAX_SEQUENCES_LAYER)) {
      mapInstance.removeLayer(PANORAMAX_SEQUENCES_LAYER)
    }
    if (mapInstance.getSource(PANORAMAX_SOURCE_ID)) {
      mapInstance.removeSource(PANORAMAX_SOURCE_ID)
    }

    mapInstance.once("render", () => {
      console.info("cypress: panoramax data removed")
    })
  }

  const togglePanoramaxLayer = () => {
    showPanoramaxLayer.value = !showPanoramaxLayer.value

    if (!showPanoramaxLayer.value) clearPanoramaxSelection()

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showPanoramaxLayer.value) {
        addPanoramaxLayer(mapInstance)
        if (mapInstance.getZoom() < PANORAMAX_ACTIVATION_ZOOM) {
          mapInstance.easeTo({ zoom: PANORAMAX_ACTIVATION_ZOOM, duration: 600 })
        }
      } else {
        removePanoramaxLayer(mapInstance)
      }
    }
  }

  const initMap = (mapId: string, layerKey: string) => {
    selectedLayer.value = getRasterLayer(layerKey)

    // markRaw: a reactive proxy around a maplibre Map breaks paint updates.
    // Style expressions read Color.rgb, a non-writable non-configurable property,
    // and a proxy cannot report the raw value for it (TypeError inside the render loop).
    mapInstancesByIds.value[mapId] = markRaw(
      new Map({
        container: mapId,
        style: loadMapStyle(selectedMapStyle.value),
        maxZoom: MAX_ZOOM + 2,
        minZoom: MIN_ZOOM,
        attributionControl: false
      })
    )

    const mapInstance = mapInstancesByIds.value[mapId]

    mapInstance.once("style.load", () => {
      mapInstance.addControl(
        new NavigationControl({ visualizePitch: true, visualizeRoll: false }),
        MAP_CONTROL_POSITION
      )
      mapInstance.addControl({ onAdd: addCenterControl, onRemove: () => {} }, MAP_CONTROL_POSITION)
      addRasterLayer(mapInstance)
      mapInstance.once("render", () => {
        console.info(`cypress: map data ${selectedMapStyle.value} loaded`)
        console.info(`cypress: layer ${selectedLayer.value.key} loaded`)
      })
    })

    mapInstance.on("moveend", () => {
      currentZoom.value = mapInstance.getZoom()
    })
    mapInstance.on("click", (e) => {
      clickCoordinates.value = { lat: e.lngLat.lat, lng: e.lngLat.lng }
    })
  }

  return {
    mapInstancesByIds,
    initMap,
    getMapInstance,
    selectedLayer,
    selectedHour,
    setLayer,
    setHour,
    hiddenClasses,
    toggleClass,
    selectedMapStyle,
    changeMapStyle,
    currentZoom,
    clickCoordinates,
    showQPVLayer,
    toggleQPVLayer,
    showBoundaryLayer,
    toggleBoundaryLayer,
    showCadastreLayer,
    toggleCadastreLayer,
    selectedCadastreParcel,
    clearCadastreSelection,
    showPanoramaxLayer,
    togglePanoramaxLayer,
    selectedPanoramaxPicture,
    clearPanoramaxSelection
  }
})
