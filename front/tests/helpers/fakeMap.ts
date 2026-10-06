/**
 * Stand-in for a maplibre `Map`, which cannot run without WebGL. It keeps the layer
 * stack in drawing order (bottom first) and rejects unknown anchors like maplibre does.
 */
export const createFakeMap = (layerIds: string[]) => ({
  layerIds,
  getLayersOrder: () => [...layerIds],
  getLayer: (id: string) => (layerIds.includes(id) ? { id } : undefined),
  addLayer: ({ id }: { id: string }, beforeId?: string) => {
    if (beforeId && !layerIds.includes(beforeId)) throw new Error(`Layer "${beforeId}" not found`)
    layerIds.splice(beforeId ? layerIds.indexOf(beforeId) : layerIds.length, 0, id)
  },
  removeLayer: (id: string) => layerIds.splice(layerIds.indexOf(id), 1),
  getSource: () => undefined,
  removeSource: () => undefined,
  easeTo: () => undefined,
  on: () => undefined,
  off: () => undefined
})
