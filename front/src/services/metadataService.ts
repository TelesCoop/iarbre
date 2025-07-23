import { useApiGet } from "../api"

export interface MetadataResponse {
  generationDate?: string
}

export const getMetadata = async (): Promise<MetadataResponse | null> => {
  try {
    const req = await useApiGet<MetadataResponse>(
      "metadata/",
      "Impossible de récupérer les métadonnées"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving metadata:", error)
    return null
  }
}
