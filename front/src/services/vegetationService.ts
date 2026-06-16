import { useApiGet } from "@/api"

export const getVegetationHeightAtPoint = async (
  lat: number,
  lng: number
): Promise<number | null> => {
  try {
    const req = await useApiGet<{ height: number | null }>(
      `tiles/vegetation-height/value/?lat=${lat}&lng=${lng}`,
      "Unable to retrieve vegetation height"
    )
    return req.data?.height ?? null
  } catch {
    return null
  }
}
