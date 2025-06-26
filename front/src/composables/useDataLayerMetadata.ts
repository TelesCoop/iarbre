import { DataType, DataTypeToLabel } from "@/utils/enum"

export interface DataLayerMetadata {
  dataType: DataType
  label: string
  icon: string
  description: string
}

export function useDataLayerMetadata() {
  const dataLayerOptions: DataLayerMetadata[] = [
    {
      dataType: DataType.PLANTABILITY,
      label: DataTypeToLabel[DataType.PLANTABILITY],
      icon: "🌱",
      description: "Potentiel de plantation d'arbres"
    },
    {
      dataType: DataType.VULNERABILITY,
      label: DataTypeToLabel[DataType.VULNERABILITY],
      icon: "🌡️",
      description: "Vulnérabilité climatique"
    },
    {
      dataType: DataType.CLIMATE_ZONE,
      label: DataTypeToLabel[DataType.CLIMATE_ZONE],
      icon: "🌍",
      description: "Zones climatiques locales"
    }
  ]

  return {
    dataLayerOptions
  }
}
