import type { LocationQuery, LocationQueryRaw } from "vue-router"
import type { MapDisplayState } from "@/types/map"
import { DEFAULT_MAP_STYLE } from "@/utils/constants"
import { DataType, MapStyle, OverlayLayer } from "@/utils/enum"
import { MAP_STYLE_OPTIONS } from "@/utils/mapStyleOptions"

const LIST_SEPARATOR = ","

const NUMERIC_FILTER_DATA_TYPES: (DataType | null)[] = [
  DataType.PLANTABILITY,
  DataType.VULNERABILITY
]

const readQueryValues = (rawValue: LocationQuery[string] | undefined): string[] =>
  [rawValue]
    .flat()
    .flatMap((value) => (value ? value.split(LIST_SEPARATOR) : []))
    .filter((value) => value !== "")

const parseFilters = (values: string[], dataType: DataType | null): (number | string)[] =>
  NUMERIC_FILTER_DATA_TYPES.includes(dataType) ? values.map(Number).filter(Number.isFinite) : values

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
    query.filters = state.filters.map(String).join(LIST_SEPARATOR)
  }
  if (state.mapStyle !== DEFAULT_MAP_STYLE) {
    query.basemap = state.mapStyle
  }
  if (state.overlayLayers.length > 0) {
    query.layers = state.overlayLayers.join(LIST_SEPARATOR)
  }

  return query
}
