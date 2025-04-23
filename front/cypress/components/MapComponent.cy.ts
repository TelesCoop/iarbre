import { createTestingPinia } from "@pinia/testing"
import { DataType } from "@/utils/enum"

import MapComponent from "@/components/map/MapComponent.vue"

describe("MapComponent", () => {
  beforeEach(() => {
    createTestingPinia({
      createSpy: cy.spy,
      stubActions: false
    })
  })
  it("renders correctly", () => {
    cy.mount(MapComponent, {
      props: {
        mapId: "default",
        modelValue: {
          lng: 45.76723,
          lat: 4.82218,
          dataType: DataType.PLANTABILITY
        }
      }
    })
  })
})
