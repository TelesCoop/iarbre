import { describe, it, expect, vi } from "vitest"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))
import { mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import ShapeLiveChip from "@/components/map/ShapeLiveChip.vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode, DataType } from "@/utils/enum"

const triangle = [
  [0, 0],
  [0.001, 0],
  [0.001, 0.001],
  [0, 0]
]

const makeMap = () => ({
  project: vi.fn(() => ({ x: 120, y: 80 })),
  on: vi.fn(),
  off: vi.fn()
})

const mountChip = () => {
  const wrapper = mount(ShapeLiveChip, {
    global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
  })
  const store = useMapStore()
  store.selectedDataType = DataType.PLANTABILITY
  store.selectionMode = SelectionMode.POLYGON
  store.shapeEditing = false
  store.liveArea = 12392
  store.mapInstancesByIds = { default: makeMap() as any }
  store.shapeDrawing.getCurrentShapeCoordinates = vi.fn(() => triangle)
  return { wrapper, store }
}

describe("ShapeLiveChip", () => {
  it("is hidden in point state", async () => {
    const { wrapper, store } = mountChip()
    store.selectionMode = SelectionMode.POINT
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-cy='shape-live-chip']").exists()).toBe(false)
  })

  it("shows the formatted area when a shape exists", async () => {
    const { wrapper } = mountChip()
    await wrapper.vm.$nextTick()
    const chip = wrapper.find("[data-cy='shape-live-chip']")
    expect(chip.exists()).toBe(true)
    expect(chip.text()).toContain("0,01 km²")
  })

  it("shows a spinner while the score is being calculated", async () => {
    const { wrapper, store } = mountChip()
    store.isCalculating = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-cy='shape-live-chip-spinner']").exists()).toBe(true)
  })

  it("warns when the area is too large", async () => {
    const { wrapper, store } = mountChip()
    store.liveArea = 20_000_000
    await wrapper.vm.$nextTick()
    const chip = wrapper.find("[data-cy='shape-live-chip']")
    expect(chip.text()).toContain("Zone trop grande")
    expect(chip.text()).not.toContain("score moyen")
  })
})
