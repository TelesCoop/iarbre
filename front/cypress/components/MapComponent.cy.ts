import { createTestingPinia } from "@pinia/testing"

import MapComponent from "@/components/map/MapComponent.vue"

describe("MapComponent", () => {
  beforeEach(() => {
    createTestingPinia({
      createSpy: cy.spy
    })
  })
  it("renders correctly", () => {
    cy.mount(MapComponent, {
      props: {
        mapId: "default"
      }
    })
  })
})
