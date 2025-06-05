import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapContextData from "@/components/contextData/MapContextData.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { PlantabilityLandUseKeys } from "../../src/types/plantability"

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

  it("should display informations correctly", () => {
    cy.window().then((win) => {
      const store = useMapStore()
      store.tileDetails = {
        plantabilityNormalizedIndice: 2,
        details: {
          top5LandUse: {
            [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 88,
            [PlantabilityLandUseKeys.ARBRES]: 60,
            [PlantabilityLandUseKeys.BATIMENTS]: 56,
            [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]: 32
          }
        },
        geolevel: "tile",
        datatype: "plantability",
        iris: 547,
        city: 63
      }
      store.selectedDataType = DataType.PLANTABILITY
    })

    // Le score affiché devrait être 7.5/10
    cy.contains("7.5/10").should("be.visible")
  })
})
