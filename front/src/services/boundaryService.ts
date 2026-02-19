import { useApiGet } from "@/api"

export const getCityBoundaries = async (): Promise<GeoJSON.FeatureCollection | null> => {
  try {
    const req = await useApiGet<GeoJSON.FeatureCollection>(
      "boundaries/cities/",
      "Impossible de récupérer les contours des communes"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving city boundaries:", error)
    return null
  }
}

export const getIrisBoundaries = async (): Promise<GeoJSON.FeatureCollection | null> => {
  try {
    const req = await useApiGet<GeoJSON.FeatureCollection>(
      "boundaries/iris/",
      "Impossible de récupérer les contours IRIS"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving IRIS boundaries:", error)
    return null
  }
}
