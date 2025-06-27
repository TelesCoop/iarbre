import { useApiGet } from "@/api"

export const getQPVData = async (): Promise<GeoJSON.FeatureCollection | null> => {
  try {
    const req = await useApiGet<GeoJSON.FeatureCollection>(
      "qpv/",
      "Impossible de récupérer les données QPV"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving QPV data:", error)
    return null
  }
}
