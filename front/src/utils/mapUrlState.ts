import type { LocationQuery, LocationQueryRaw } from "vue-router"
import type { MapDisplayState } from "@/types/map"
import { DEFAULT_MAP_STYLE } from "@/utils/constants"
import { DataType, MapStyle, OverlayLayer } from "@/utils/enum"
import { MAP_STYLE_OPTIONS } from "@/utils/mapStyleOptions"
import { BIOSPHERE_CLASSES, BIOSPHERE_DETAIL_CLASSES } from "@/utils/biosphere_functional_integrity"

const LIST_SEPARATOR = ","

const NUMERIC_FILTER_DATA_TYPES: (DataType | null)[] = [
  DataType.PLANTABILITY,
  DataType.VULNERABILITY
]

const BIOSPHERE_ALL_CLASSES = [...BIOSPHERE_CLASSES, ...BIOSPHERE_DETAIL_CLASSES]

const encodeFilter = (value: number | string): string => {
  const biosphereClass = BIOSPHERE_ALL_CLASSES.find((c) => c.label === value)
  return biosphereClass ? `${biosphereClass.min}-${biosphereClass.max}` : String(value)
}

const decodeBiosphereFilter = (value: string): string =>
  BIOSPHERE_ALL_CLASSES.find((c) => `${c.min}-${c.max}` === value)?.label ?? value

const readQueryValues = (rawValue: LocationQuery[string] | undefined): string[] =>
  [rawValue]
    .flat()
    .flatMap((value) => (value ? value.split(LIST_SEPARATOR) : []))
    .filter((value) => value !== "")

const parseFilters = (values: string[], dataType: DataType | null): (number | string)[] => {
  if (NUMERIC_FILTER_DATA_TYPES.includes(dataType)) {
    return values.map(Number).filter(Number.isFinite)
  }
  if (dataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY) {
    return values.map(decodeBiosphereFilter)
  }
  return values
}

const isSelectableMapStyle = (value: string): value is MapStyle =>
  MAP_STYLE_OPTIONS.some((option) => option.value === value)

const isOverlayLayer = (value: string): value is OverlayLayer =>
  Object.values<string>(OverlayLayer).includes(value)

export const parseMapDisplayState = (
  query: LocationQuery,
  dataType: DataType | null
): MapDisplayState => ({
  filters: parseFilters(readQueryValues(query.filters), dataType),
  mapStyle: readQueryValues(query.basemap).find(isSelectableMapStyle) ?? DEFAULT_MAP_STYLE,
  overlayLayers: readQueryValues(query.layers).filter(isOverlayLayer)
})

export const buildMapDisplayQuery = (state: MapDisplayState): LocationQueryRaw => {
  const query: LocationQueryRaw = {}

  if (state.filters.length > 0) {
    query.filters = state.filters.map(encodeFilter).join(LIST_SEPARATOR)
  }
  if (state.mapStyle !== DEFAULT_MAP_STYLE) {
    query.basemap = state.mapStyle
  }
  if (state.overlayLayers.length > 0) {
    query.layers = state.overlayLayers.join(LIST_SEPARATOR)
  }

  return query
}
