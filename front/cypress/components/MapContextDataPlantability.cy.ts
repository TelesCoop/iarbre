/// <reference types="cypress" />
import MapContextData from "@/components/contextData/MapContextData.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { PlantabilityLandUseKeys, PlantabilityMetaCategory } from "@/types/plantability"
import { GeoLevel } from "@/utils/enum"

describe("MapContextData", () => {
  beforeEach(() => {
    cy.mount(MapContextData, {
      props: {
        data: DataType
      }
    })
  })

  it("should display component when tileDetails and PLANTABILITY datatype are set", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.contextData.data = { plantabilityNormalizedIndice: 8.5 }
      store.selectedDataType = DataType.PLANTABILITY
    })
    cy.get('[data-cy="map-context-data"]').should("be.visible")
  })

  it("display empty message when no data is available", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.contextData.data = null
      store.selectedDataType = DataType.PLANTABILITY
    })
    cy.contains("Zommez et cliquez sur un carreau").should("be.visible")
  })

  it("should display informations correctly", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.contextData.data = {
        plantabilityNormalizedIndice: 2,
        details: {
          top5LandUse: {
            [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 88,
            [PlantabilityLandUseKeys.BATIMENTS]: 56
          }
        },
        geolevel: GeoLevel.TILE,
        datatype: DataType.PLANTABILITY,
        iris: 547,
        city: 63
      }
      store.selectedDataType = DataType.PLANTABILITY
    })
    cy.contains("2/10").should("be.visible")

    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`).should("exist")
    cy.contains("Bâtiments").should("be.visible")
    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`)
      .find(".accordion-header")
      .click()
    cy.contains("Proximité façade").should("be.visible")
  })
})
