import { DataType, GeoLevel } from "@/utils/enum"
import { Map, type GeoJSONSource, type DataDrivenPropertyValueSpecification } from "maplibre-gl"

// fill-extrusion has no stroke/outline paint property. To fake one, turn each
// edge of the polygon into a thin quad straddling that edge, then render all
// the quads as their own white fill-extrusion layer at the tile's height: a
// ring of thin vertical walls around the tile, with no flat top to read as a cap.
export const buildSelectionWallPolygons = (
  geometry: { type: string; coordinates: any },
  halfWidthMeters: number
): number[][][][] => {
  const METERS_PER_DEGREE_LAT = 111320

  const rings: number[][][] =
    geometry.type === "Polygon"
      ? geometry.coordinates
      : geometry.type === "MultiPolygon"
        ? geometry.coordinates.flat()
        : []

  const quads: number[][][][] = []

  for (const ring of rings) {
    for (let i = 0; i < ring.length - 1; i++) {
      const [lng1, lat1] = ring[i]
      const [lng2, lat2] = ring[i + 1]
      const latRef = (lat1 + lat2) / 2
      const lngPerMeter = 1 / (METERS_PER_DEGREE_LAT * Math.cos((latRef * Math.PI) / 180))
      const latPerMeter = 1 / METERS_PER_DEGREE_LAT

      // Edge vector in an approximate local meter frame, then its perpendicular,
      // so the quad's width reads as a constant physical thickness regardless
      // of latitude or edge orientation.
      const dx = (lng2 - lng1) / lngPerMeter
      const dy = (lat2 - lat1) / latPerMeter
      const length = Math.hypot(dx, dy)
      if (length === 0) continue

      const nx = (-dy / length) * halfWidthMeters
      const ny = (dx / length) * halfWidthMeters
      const offsetLng = nx * lngPerMeter
      const offsetLat = ny * latPerMeter

      const p1a = [lng1 + offsetLng, lat1 + offsetLat]
      const p2a = [lng2 + offsetLng, lat2 + offsetLat]
      const p2b = [lng2 - offsetLng, lat2 - offsetLat]
      const p1b = [lng1 - offsetLng, lat1 - offsetLat]

      quads.push([[p1a, p2a, p2b, p1b, p1a]])
    }
  }

  return quads
}

const SELECTION_WALL_SOURCE = "ifb-selection-wall-source"
const SELECTION_WALL_LAYER = "ifb-selection-wall-layer"
// Half-width of the wall, in meters, on either side of the tile's edge.
// The quad straddles the edge, so only the outer half is actually visible
// (the inner half is buried inside the tile itself) — kept fairly wide so
// that visible half still reads clearly.
const SELECTION_WALL_HALF_WIDTH_M = 1

// Draws the white "casing" wall around a selected 3D tile: a fill-extrusion
// layer built from buildSelectionWallPolygons, using the same height
// expression as the real tile layer so it tops out at the same height, and
// carrying the tile's own properties so that expression can read them.
export const showSelectionWall3D = (
  map: Map,
  geometry: any,
  properties: Record<string, any>,
  heightExpression: DataDrivenPropertyValueSpecification<number>
) => {
  if (!geometry) return

  const wallCollection = {
    type: "FeatureCollection" as const,
    features: buildSelectionWallPolygons(geometry, SELECTION_WALL_HALF_WIDTH_M).map(
      (coordinates) => ({
        type: "Feature" as const,
        geometry: { type: "Polygon" as const, coordinates },
        properties: { ...properties }
      })
    )
  }

  const source = map.getSource(SELECTION_WALL_SOURCE) as GeoJSONSource | undefined
  if (source) {
    source.setData(wallCollection)
  } else {
    map.addSource(SELECTION_WALL_SOURCE, { type: "geojson", data: wallCollection })
  }

  if (!map.getLayer(SELECTION_WALL_LAYER)) {
    map.addLayer({
      id: SELECTION_WALL_LAYER,
      type: "fill-extrusion",
      source: SELECTION_WALL_SOURCE,
      paint: {
        "fill-extrusion-color": "#FFFFFF",
        "fill-extrusion-height": heightExpression,
        "fill-extrusion-base": 0,
        "fill-extrusion-opacity": 1,
        "fill-extrusion-vertical-gradient": false
      }
    })
  } else {
    map.setPaintProperty(SELECTION_WALL_LAYER, "fill-extrusion-height", heightExpression)
  }
}

export const clearSelectionWall3D = (map: Map) => {
  if (map.getLayer(SELECTION_WALL_LAYER)) {
    map.removeLayer(SELECTION_WALL_LAYER)
  }
  if (map.getSource(SELECTION_WALL_SOURCE)) {
    map.removeSource(SELECTION_WALL_SOURCE)
  }
}

const SELECTION_OUTLINE_SOURCE = "ifb-selection-outline-source"
const SELECTION_OUTLINE_LAYER = "ifb-selection-outline-layer"

// Draws the white outline around a selected 2D tile, straight from its
// stored geometry (own source + layer, same idea as the 3D wall above).
export const showSelectionOutline2D = (map: Map, geometry: any) => {
  if (!geometry) return

  const outline = { type: "Feature" as const, geometry, properties: {} }
  const source = map.getSource(SELECTION_OUTLINE_SOURCE) as GeoJSONSource | undefined

  if (source) {
    source.setData(outline)
  } else {
    map.addSource(SELECTION_OUTLINE_SOURCE, { type: "geojson", data: outline })
  }

  if (!map.getLayer(SELECTION_OUTLINE_LAYER)) {
    map.addLayer({
      id: SELECTION_OUTLINE_LAYER,
      type: "line",
      source: SELECTION_OUTLINE_SOURCE,
      paint: {
        "line-color": "#FFFFFF",
        "line-width": 4
      }
    })
  }
}

export const clearSelectionOutline2D = (map: Map) => {
  if (map.getLayer(SELECTION_OUTLINE_LAYER)) {
    map.removeLayer(SELECTION_OUTLINE_LAYER)
  }
  if (map.getSource(SELECTION_OUTLINE_SOURCE)) {
    map.removeSource(SELECTION_OUTLINE_SOURCE)
  }
}

export const getSourceId = (datatype: DataType, geolevel: GeoLevel) => {
  return `${geolevel}-${datatype}-source`
}

export const getLayerId = (datatype: DataType, geolevel: GeoLevel) => {
  return `${geolevel}-${datatype}-layer`
}

export const extractFeatures = (features: Array<any>, datatype: DataType, geolevel: GeoLevel) => {
  if (!features) return undefined

  const feature = features.find(
    (feature: any) => feature.layer.id === getLayerId(datatype, geolevel)
  )

  return feature || undefined
}

export const extractFeatureProperty = (
  features: Array<any>,
  datatype: DataType,
  geolevel: GeoLevel,
  propertyName?: string
) => {
  const feature = extractFeatures(features, datatype, geolevel)
  if (!feature) return undefined
  return propertyName ? feature.properties[propertyName] : feature.properties
}

export const extractFeatureProperties = (
  features: Array<any>,
  datatype: DataType,
  geolevel: GeoLevel
) => {
  return extractFeatureProperty(features, datatype, geolevel)
}
