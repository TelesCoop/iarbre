import { useApiGet } from "@/api"
import type { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"

export const getTileDetails = async (
  id: string,
  dataType: DataType
): Promise<
  PlantabilityData | VulnerabilityData | ClimateData | PlantabilityVulnerabilityData | null
> => {
  try {
    const req = await useApiGet(
      `tiles/${dataType}/${id}/`,
      `Impossible de récupérer les informations de la tuile avec l'id ${id}`
    )
    return req.data as
      | PlantabilityData
      | VulnerabilityData
      | ClimateData
      | PlantabilityVulnerabilityData
  } catch (error) {
    console.error("Error retrieving tile details:", error)
    return null
  }
}
