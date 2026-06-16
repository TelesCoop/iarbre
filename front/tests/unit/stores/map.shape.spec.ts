import { describe, it, expect, beforeEach, vi } from "vitest"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))
import { setActivePinia, createPinia } from "pinia"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"

describe("map store shape state machine", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("starts in point state", () => {
    const store = useMapStore()
    expect(store.drawingState).toBe("point")
  })

  it("enterShapeMode moves to drawing state", () => {
    const store = useMapStore()
    store.enterShapeMode(SelectionMode.POLYGON)
    expect(store.selectionMode).toBe(SelectionMode.POLYGON)
    expect(store.drawingState).toBe("drawing")
  })

  it("markShapeFinished moves to editing state", () => {
    const store = useMapStore()
    store.enterShapeMode(SelectionMode.POLYGON)
    store.markShapeFinished()
    expect(store.drawingState).toBe("editing")
  })

  it("startNewShape returns from editing to drawing", () => {
    const store = useMapStore()
    store.enterShapeMode(SelectionMode.POLYGON)
    store.markShapeFinished()
    store.startNewShape(SelectionMode.CIRCLE)
    expect(store.drawingState).toBe("drawing")
    expect(store.selectionMode).toBe(SelectionMode.CIRCLE)
  })

  it("exitShapeMode resets to point and clears live area", () => {
    const store = useMapStore()
    store.enterShapeMode(SelectionMode.POLYGON)
    store.markShapeFinished()
    store.exitShapeMode()
    expect(store.drawingState).toBe("point")
    expect(store.selectionMode).toBe(SelectionMode.POINT)
    expect(store.liveArea).toBeNull()
  })

  it("startNewShape clears a previously set live area", () => {
    const store = useMapStore()
    store.enterShapeMode(SelectionMode.POLYGON)
    store.liveArea = 12345
    store.startNewShape(SelectionMode.CIRCLE)
    expect(store.liveArea).toBeNull()
  })

  it("flags areas above the limit as too large", () => {
    const store = useMapStore()
    store.liveArea = 5_000_000
    expect(store.isAreaTooLarge).toBe(false)
    store.liveArea = 20_000_000
    expect(store.isAreaTooLarge).toBe(true)
    store.liveArea = null
    expect(store.isAreaTooLarge).toBe(false)
  })
})
