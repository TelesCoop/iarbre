import { createTestingPinia } from "@pinia/testing"
import { useMapStore } from "@/stores/map"

import MapComponent from "@/components/map/MapComponent.vue"

describe("Component:MapComponent", () => {
  beforeEach(async () => {
    createTestingPinia({
      createSpy: cy.spy
    })
    cy.wrap(useMapStore()).as("map")
  })
  it("renders correctly", () => {
    cy.mount(MapComponent)
  })
})
