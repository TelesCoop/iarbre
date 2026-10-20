import { useApiGet } from "@/api"
import type { PublicBuildingCategory } from "@/utils/enum"

export interface PublicBuildingProperties {
  name: string | null
  category: PublicBuildingCategory
  nature: string
  natureDetaillee: string | null
  fictif: boolean
  studentCount: number | null
  educationPriority: string | null
  capacity: number | null
}

export const getPublicBuildingsData = async (): Promise<GeoJSON.FeatureCollection<
  GeoJSON.Geometry,
  PublicBuildingProperties
> | null> => {
  try {
    const req = await useApiGet<
      GeoJSON.FeatureCollection<GeoJSON.Geometry, PublicBuildingProperties>
    >("public-buildings/", "Impossible de récupérer les bâtiments publics")
    return req.data || null
  } catch (error) {
    console.error("Error retrieving public buildings data:", error)
    return null
  }
}
