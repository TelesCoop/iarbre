export enum GeoLevel {
  TILE = "tile",
  LCZ = "lcz"
}

export enum DataType {
  PLANTABILITY = "plantability",
  LOCAL_CLIMATE_ZONES = "lcz"
}

export enum ScoreLabelSize {
  SMALL = "small",
  HUGE = "huge"
}
export const DataTypeToLabel: Record<DataType, string> = {
  [DataType.PLANTABILITY]: "Plantabilité",
  [DataType.LOCAL_CLIMATE_ZONES]: "Zones climatiques locales"
}
