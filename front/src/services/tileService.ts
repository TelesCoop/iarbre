import { useApiGet } from "@/api"
import type { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"

export const getTileDetails = async (
  id: string,
  dataType: DataType
): Promise<PlantabilityData | VulnerabilityData | null> => {
  try {
    const req = await useApiGet(
      `tiles/${dataType}/${id}/`,
      `Impossible de récupérer les informations de la tuile avec l'id ${id}`
    )
    return req.data as PlantabilityData | VulnerabilityData
  } catch (error) {
    console.error("Error retrieving tile details:", error)
    return null
  }
}
