import type { PlantabilityTile } from "@/types/plantability"
import { useApiGet } from "@/api"
import type { DataType } from "@/utils/enum"

export const getTileDetails = async (
  id: string,
  dataType: DataType
): Promise<PlantabilityTile | null> => {
  try {
    const req = await useApiGet(
      `tiles/${dataType}/${id}/`,
      `Impossible de récupérer les informations de la tuile avec l'id ${id}`
    )
    return req.data as PlantabilityTile
  } catch (error) {
    console.error("Error retrieving tile details:", error)
    return null
  }
}
