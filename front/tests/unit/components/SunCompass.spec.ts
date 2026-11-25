import { describe, it, expect, vi } from "vitest"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))
import { mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import SunCompass from "@/components/map/legend/SunCompass.vue"
import { useMapStore } from "@/stores/map"

const sunRotation = (wrapper: ReturnType<typeof mount>) =>
  Number(
    /rotate\(([-\d.]+)/.exec(
      wrapper.get('[data-cy="sun-compass-sun"]').attributes("transform")!
    )![1]
  )

describe("SunCompass", () => {
  it("names the sun direction for the hour and turns with the map", async () => {
    const wrapper = mount(SunCompass, {
      global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
    })
    const store = useMapStore()
    store.rasterHour = 16
    store.currentBearing = 0
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain("Sud-ouest")
    expect(wrapper.attributes("aria-label")).toContain("à 16h")
    const northUp = sunRotation(wrapper)

    store.currentBearing = 90
    await wrapper.vm.$nextTick()
    expect(sunRotation(wrapper)).toBeCloseTo(northUp - 90)

    store.rasterHour = 20
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain("Ouest")
    expect(wrapper.attributes("aria-label")).toContain("à 20h")
  })
})
