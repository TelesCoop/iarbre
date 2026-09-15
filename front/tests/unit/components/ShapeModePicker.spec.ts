import { describe, it, expect, vi } from "vitest"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))

import { mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import ShapeModePicker from "@/components/map/ShapeModePicker.vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode, DataType } from "@/utils/enum"

const mountPicker = (dataType = DataType.PLANTABILITY) => {
  const wrapper = mount(ShapeModePicker, {
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn })],
      stubs: {
        SelectionModeButton: {
          name: "SelectionModeButton",
          template:
            '<button :disabled="disabled" @click="!disabled && $emit(\'select\', mode)"></button>',
          props: ["mode", "icon", "label", "active", "disabled"]
        }
      }
    }
  })
  const store = useMapStore()
  store.selectedDataType = dataType
  return { wrapper, store }
}

describe("ShapeModePicker", () => {
  it("renders one button per selection mode", () => {
    const { wrapper } = mountPicker()
    expect(wrapper.findAll("button")).toHaveLength(5)
  })

  it("calls enterShapeMode when a shape is picked from point state", async () => {
    const { wrapper, store } = mountPicker()
    // drawingState defaults to "point"
    await wrapper.findAll("button")[1].trigger("click")
    expect(store.enterShapeMode).toHaveBeenCalledWith(SelectionMode.POLYGON)
  })

  it("calls exitShapeMode when the point mode is picked", async () => {
    const { wrapper, store } = mountPicker()
    await wrapper.findAll("button")[0].trigger("click")
    expect(store.exitShapeMode).toHaveBeenCalled()
  })

  it("calls startNewShape when picking a shape while editing", async () => {
    const { wrapper, store } = mountPicker()
    store.selectionMode = SelectionMode.RECTANGLE
    store.shapeEditing = true
    await wrapper.vm.$nextTick()
    await wrapper.findAll("button")[1].trigger("click")
    expect(store.startNewShape).toHaveBeenCalledWith(SelectionMode.POLYGON)
  })

  it("disables non-point shapes for climate zone", async () => {
    const { wrapper } = mountPicker(DataType.CLIMATE_ZONE)
    await wrapper.vm.$nextTick()
    const buttons = wrapper.findAllComponents({ name: "SelectionModeButton" })
    expect(buttons[0].props("disabled")).toBe(false)
    expect(buttons[1].props("disabled")).toBe(true)
  })
})
