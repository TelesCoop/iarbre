import { describe, it, expect, vi } from "vitest"
import { mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import ShapeToolbar from "@/components/map/ShapeToolbar.vue"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { SelectionMode } from "@/utils/enum"
import { formatArea } from "@/utils/geo"

const routerPush = vi.hoisted(() => vi.fn())

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))
vi.mock("vue-router", () => ({ useRouter: () => ({ push: routerPush }) }))

const mountToolbar = () => {
  const wrapper = mount(ShapeToolbar, {
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn })],
      directives: { tooltip: {} },
      stubs: {
        ShapeModePicker: true,
        AppButton: { template: "<button><slot /></button>" },
        IconClose: true
      }
    }
  })
  return { wrapper, store: useMapStore(), zoneStore: useZoneStore() }
}

const openPanel = (wrapper: ReturnType<typeof mountToolbar>["wrapper"]) =>
  wrapper.find("[data-cy='shape-toolbar-toggle']").trigger("click")

describe("ShapeToolbar disclosure", () => {
  it("renders only the toggle, panel hidden, by default", () => {
    const { wrapper } = mountToolbar()
    expect(wrapper.find("[data-cy='shape-toolbar-toggle']").exists()).toBe(true)
    expect(wrapper.find("#shape-toolbar-panel").exists()).toBe(false)
  })

  it("opens the panel when the toggle is clicked", async () => {
    const { wrapper } = mountToolbar()
    await openPanel(wrapper)
    expect(wrapper.find("#shape-toolbar-panel").exists()).toBe(true)
  })

  it("closing the panel only hides it, without erasing the selection", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.shapeEditing = true
    await openPanel(wrapper)
    expect(wrapper.find("#shape-toolbar-panel").exists()).toBe(true)
    await openPanel(wrapper)
    expect(wrapper.find("#shape-toolbar-panel").exists()).toBe(false)
    expect(store.exitShapeMode).not.toHaveBeenCalled()
  })
})

describe("ShapeToolbar contextual actions (panel open)", () => {
  it("shows the finish action while drawing a polygon", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.shapeEditing = false
    await openPanel(wrapper)
    expect(wrapper.find("[data-cy='shape-finish']").exists()).toBe(true)
  })

  it("does not show finish action while drawing a rectangle", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.RECTANGLE
    store.shapeEditing = false
    await openPanel(wrapper)
    expect(wrapper.find("[data-cy='shape-finish']").exists()).toBe(false)
  })

  it("shows the new-shape action while editing", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.shapeEditing = true
    await openPanel(wrapper)
    expect(wrapper.find("[data-cy='shape-new']").exists()).toBe(true)
  })

  it("mentions vertices in the edit hint for a polygon", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.shapeEditing = true
    await openPanel(wrapper)
    expect(wrapper.find("#shape-toolbar-panel").text()).toContain("sommets")
  })

  it("uses a vertex-free edit hint for a circle", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.CIRCLE
    store.shapeEditing = true
    await openPanel(wrapper)
    expect(wrapper.find("#shape-toolbar-panel").text()).not.toContain("sommets")
  })

  it("triggers finishCurrentPolygon when finish is clicked", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.shapeEditing = false
    store.shapeDrawing.finishCurrentPolygon = vi.fn()
    await openPanel(wrapper)
    await wrapper.find("[data-cy='shape-finish']").trigger("click")
    expect(store.shapeDrawing.finishCurrentPolygon).toHaveBeenCalled()
  })

  it("triggers exitShapeMode when clear is clicked", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    await openPanel(wrapper)
    await wrapper.find("[data-cy='shape-clear']").trigger("click")
    expect(store.exitShapeMode).toHaveBeenCalled()
  })

  it("hides contextual actions in point state", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POINT
    await openPanel(wrapper)
    expect(wrapper.find("[data-cy='shape-clear']").exists()).toBe(false)
  })
})

describe("ShapeToolbar finished zone", () => {
  it("opens the panel with the zone area once the shape is finished", async () => {
    const { wrapper, store } = mountToolbar()
    store.selectionMode = SelectionMode.POLYGON
    store.liveArea = 12000

    store.shapeEditing = true
    await wrapper.vm.$nextTick()

    expect(wrapper.find("#shape-toolbar-panel").text()).toContain(formatArea(12000))
  })

  it("opens the zone dashboard from the panel", async () => {
    const { wrapper, store, zoneStore } = mountToolbar()
    const polygon = { type: "Polygon", coordinates: [] }
    store.selectionMode = SelectionMode.POLYGON
    vi.mocked(store.getDrawnPolygon).mockReturnValue(polygon as never)
    store.shapeEditing = true
    await wrapper.vm.$nextTick()

    await wrapper.find("[data-cy='zone-dashboard-cta']").trigger("click")

    expect(zoneStore.setZone).toHaveBeenCalledWith(polygon)
    expect(store.exitShapeMode).toHaveBeenCalled()
    expect(routerPush).toHaveBeenCalledWith({ name: "dashboard" })
  })
})
