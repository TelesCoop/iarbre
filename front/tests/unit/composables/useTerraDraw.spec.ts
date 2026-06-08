import { describe, it, expect, vi, beforeEach } from "vitest"

const finishHandlers: Array<(id: string | number) => void> = []
const changeHandlers: Array<(ids: (string | number)[], type: string) => void> = []
const terraDrawMock = {
  start: vi.fn(),
  stop: vi.fn(),
  clear: vi.fn(),
  setMode: vi.fn(),
  selectFeature: vi.fn(),
  removeFeatures: vi.fn(),
  updateModeOptions: vi.fn(),
  getSnapshot: vi.fn(() => [] as any[]),
  on: vi.fn((event: string, cb: any) => {
    if (event === "finish") finishHandlers.push(cb)
    if (event === "change") changeHandlers.push(cb)
  })
}

vi.mock("terra-draw", () => {
  class Stub {
    constructor() {
      return terraDrawMock as any
    }
  }
  return {
    TerraDraw: vi.fn(() => terraDrawMock),
    TerraDrawPointMode: Stub,
    TerraDrawPolygonMode: Stub,
    TerraDrawRectangleMode: Stub,
    TerraDrawAngledRectangleMode: Stub,
    TerraDrawCircleMode: Stub,
    TerraDrawFreehandMode: Stub,
    TerraDrawSelectMode: Stub
  }
})
vi.mock("terra-draw-maplibre-gl-adapter", () => ({ TerraDrawMapLibreGLAdapter: vi.fn() }))

import { useShapeDrawing } from "@/composables/useTerraDraw"

const dispatchEvent = vi.fn()
const fakeMap = { getCanvas: () => ({ dispatchEvent }) } as any

describe("useShapeDrawing finish behaviour", () => {
  beforeEach(() => {
    finishHandlers.length = 0
    changeHandlers.length = 0
    vi.clearAllMocks()
    terraDrawMock.getSnapshot.mockReturnValue([])
  })

  it("switches to select mode and selects the feature on finish (without clearing)", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    finishHandlers[0]("feat-1")
    expect(terraDrawMock.setMode).toHaveBeenCalledWith("select")
    expect(terraDrawMock.selectFeature).toHaveBeenCalledWith("feat-1")
    expect(terraDrawMock.clear).not.toHaveBeenCalled()
  })

  it("invokes the onShapeFinished callback on finish", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    const onFinished = vi.fn()
    drawing.onShapeFinished(onFinished)
    finishHandlers[0]("feat-1")
    expect(onFinished).toHaveBeenCalledTimes(1)
  })

  it("invokes the onShapeChanged callback on geometry change but not on styling", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    const onChanged = vi.fn()
    drawing.onShapeChanged(onChanged)
    changeHandlers[0](["feat-1"], "update")
    expect(onChanged).toHaveBeenCalledTimes(1)
    changeHandlers[0](["feat-1"], "styling")
    expect(onChanged).toHaveBeenCalledTimes(1)
  })

  it("finishCurrentPolygon dispatches Enter only in polygon mode", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    drawing.setMode("polygon" as any)
    drawing.finishCurrentPolygon()
    expect(dispatchEvent).toHaveBeenCalledTimes(1)
    const evt = dispatchEvent.mock.calls[0][0] as KeyboardEvent
    expect(evt.key).toBe("Enter")
  })

  it("finishCurrentPolygon does nothing outside polygon mode", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    drawing.setMode("circle" as any)
    drawing.finishCurrentPolygon()
    expect(dispatchEvent).not.toHaveBeenCalled()
  })

  it("getCurrentShapeCoordinates returns the polygon ring or null", () => {
    const drawing = useShapeDrawing()
    drawing.initDraw(fakeMap)
    expect(drawing.getCurrentShapeCoordinates()).toBeNull()
    terraDrawMock.getSnapshot.mockReturnValue([
      {
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [0, 0],
              [1, 0],
              [1, 1]
            ]
          ]
        }
      }
    ])
    expect(drawing.getCurrentShapeCoordinates()).toEqual([
      [0, 0],
      [1, 0],
      [1, 1]
    ])
  })
})
