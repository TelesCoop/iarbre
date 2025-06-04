import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapContextData from "@/components/contextData/MapContextData.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("MapContextData", () => {
  beforeEach(() => {
    const pinia = createPinia()

    mount(MapContextData, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: DataType
      }
    })
  })

  it("should display component when tileDetails and PLANTABILITY datatype are set", () => {
    cy.window().then((win) => {
      const store = useMapStore()
      store.tileDetails = { plantabilityNormalizedIndice: 8.5 }
      store.selectedDataType = DataType.PLANTABILITY
    })
    cy.get('[data-cy="map-context-data"]').should("be.visible")
  })
  it("should hide component when tileDetails is null", () => {
    cy.window().then((win) => {
      const store = useMapStore()
      store.tileDetails = null
      store.selectedDataType = DataType.PLANTABILITY
    })

    cy.get('[data-cy="map-context-data"]').should("not.exist")
  })

  it("should display correct score calculation", () => {
    mount(MapContextData, {
      props: {
        data: mockData
      }
    })

    // Le score affiché devrait être 7.5/10
    cy.contains("7.5/10").should("be.visible")
  })
})
