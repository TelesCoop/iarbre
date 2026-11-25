import { describe, it, expect, vi } from "vitest"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))
import { mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import HourlyRasterToggle from "@/components/contextTools/HourlyRasterToggle.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

const mountToggle = (dataType: DataType) => {
  const wrapper = mount(HourlyRasterToggle, {
    global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
  })
  const store = useMapStore()
  store.selectedDataType = dataType
  return { wrapper, store }
}

describe("HourlyRasterToggle", () => {
  it("switches between comfort and shadow", async () => {
    const { wrapper, store } = mountToggle(DataType.PET)
    await wrapper.vm.$nextTick()
    const toggle = wrapper.get('[role="switch"]')
    expect(toggle.attributes("aria-checked")).toBe("false")

    await toggle.trigger("click")
    expect(store.changeDataType).toHaveBeenLastCalledWith(DataType.SHADOW)

    store.selectedDataType = DataType.SHADOW
    await wrapper.vm.$nextTick()
    expect(toggle.attributes("aria-checked")).toBe("true")
    await toggle.trigger("click")
    expect(store.changeDataType).toHaveBeenLastCalledWith(DataType.PET)
  })

  it("selects a layer from its label and ignores the active one", async () => {
    const { wrapper, store } = mountToggle(DataType.PET)
    await wrapper.vm.$nextTick()

    await wrapper.get(`#hourly-raster-toggle-${DataType.PET}`).trigger("click")
    expect(store.changeDataType).not.toHaveBeenCalled()

    await wrapper.get(`#hourly-raster-toggle-${DataType.SHADOW}`).trigger("click")
    expect(store.changeDataType).toHaveBeenCalledWith(DataType.SHADOW)
  })
})
