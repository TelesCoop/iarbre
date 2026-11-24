import { describe, it, expect, vi, beforeEach } from "vitest"
import { ref } from "vue"
import { useContextData } from "@/composables/useContextData"
import { DataType, GeoLevel } from "@/utils/enum"

const useApiGetMock = vi.hoisted(() => vi.fn())

vi.mock("@/api", () => ({ useApiGet: useApiGetMock, useApiPost: vi.fn() }))

const POINT = {
  id: "1m-2843-1693",
  plantabilityIndice: -1.2,
  plantabilityNormalizedIndice: 4,
  details: { top5LandUse: { Parkings: 60 } }
}

describe("useContextData on plantability 2026 layers", () => {
  beforeEach(() => {
    useApiGetMock.mockReset()
  })

  it("loads the clicked point of the selected grid", async () => {
    useApiGetMock.mockResolvedValue({ data: POINT })
    const contextData = useContextData(ref(DataType.PLANTABILITY_2026_1M))

    await contextData.setData("45.77,4.88", undefined, undefined, undefined, undefined, 45.77, 4.88)

    expect(useApiGetMock).toHaveBeenCalledWith(
      "tiles/plantability-2026/value/?grid=1&lat=45.77&lng=4.88"
    )
    expect(contextData.data.value).toEqual({
      ...POINT,
      geolevel: GeoLevel.TILE,
      datatype: DataType.PLANTABILITY_2026_1M
    })
  })

  it("clears the previous point when clicking outside the raster", async () => {
    useApiGetMock.mockResolvedValueOnce({ data: POINT })
    useApiGetMock.mockResolvedValueOnce({ data: undefined, error: { detail: "Not found" } })
    const contextData = useContextData(ref(DataType.PLANTABILITY_2026_5M))

    await contextData.setData("45.77,4.88", undefined, undefined, undefined, undefined, 45.77, 4.88)
    await contextData.setData("0,0", undefined, undefined, undefined, undefined, 0, 0)

    expect(useApiGetMock).toHaveBeenLastCalledWith(
      "tiles/plantability-2026/value/?grid=5&lat=0&lng=0"
    )
    expect(contextData.data.value).toBeNull()
  })
})
