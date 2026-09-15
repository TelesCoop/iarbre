import { useApiGet } from "@/api"
import type { LandCoverRecord } from "@/types/biosphereIntegrity"

export const getBiosphereLandCoverAtPoint = async (
  lat: number,
  lng: number
): Promise<LandCoverRecord[] | null> => {
  try {
    const req = await useApiGet<LandCoverRecord[]>(
      `biosphere/land-cover-at-point/?lat=${lat}&lng=${lng}`,
      "Unable to retrieve land cover at point"
    )
    return req.data ?? null
  } catch (error) {
    console.error("Error retrieving land cover at point:", error)
    return null
  }
}
