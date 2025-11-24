import { useApiGet, useApiPost } from "@/api"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type {
  PlantabilityScoresResponse,
  VulnerabilityScoresResponse,
  LczScoresResponse
} from "@/types/api"

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

export const getScoresInPolygon = async (
  polygonCoordinates: [number, number][],
  dataType: DataType
): Promise<PlantabilityData | VulnerabilityData | ClimateData | null> => {
  try {
    // Créer le GeoJSON polygon
    const polygon = {
      type: "Polygon",
      coordinates: [polygonCoordinates]
    }

    const req = await useApiPost<
      PlantabilityScoresResponse | VulnerabilityScoresResponse | LczScoresResponse
    >(
      `tiles/${dataType}/in-polygon/`,
      polygon,
      `Impossible de récupérer les scores dans le polygone`
    )

    if (!req.data) return null

    // Transform backend response to match expected types
    if (dataType === DataType.PLANTABILITY) {
      const data = req.data as PlantabilityScoresResponse
      console.log("Polygon scores response:", data)
      console.log("iris_codes:", data.irisCodes, "city_codes:", data.cityCodes)
      return {
        id: `polygon-${data.count}`,
        plantabilityNormalizedIndice: data.plantabilityNormalizedIndice,
        plantabilityIndice: data.plantabilityIndice,
        distribution: data.distribution,
        geolevel: "tile" as any,
        datatype: dataType,
        irisCodes: data.irisCodes,
        cityCodes: data.cityCodes
      } as PlantabilityData
    } else if (dataType === DataType.VULNERABILITY) {
      const data = req.data as VulnerabilityScoresResponse
      return {
        id: data.count,
        vulnerabilityIndexDay: data.vulnerabilityIndexDay,
        vulnerabilityIndexNight: data.vulnerabilityIndexNight,
        capafIndexDay: 0,
        capafIndexNight: 0,
        expoIndexDay: 0,
        expoIndexNight: 0,
        sensibiltyIndexDay: 0,
        sensibiltyIndexNight: 0,
        geometry: "",
        mapGeometry: "",
        details: null,
        geolevel: "tile" as any,
        datatype: dataType
      } as VulnerabilityData
    } else if (dataType === DataType.CLIMATE_ZONE) {
      const data = req.data as LczScoresResponse
      return {
        id: data.count,
        lczIndex: data.lcz_primary || 0,
        lczDescription: `Zone climatique ${data.lcz_primary || "mixte"}`,
        geometry: "",
        mapGeometry: "",
        details: {
          hre: 0,
          are: 0,
          bur: 0,
          ror: 0,
          bsr: 0,
          war: 0,
          ver: 0,
          vhr: 0
        },
        geolevel: "tile" as any,
        datatype: dataType
      } as ClimateData
    }

    return null
  } catch (error) {
    console.error("Error retrieving scores in polygon:", error)
    return null
  }
}
