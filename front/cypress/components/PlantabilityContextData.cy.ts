import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapContextData from "@/components/contextData/MapContextData.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { PlantabilityLandUseKeys, PlantabilityMetaCategory } from "@/types/plantability"
import { GeoLevel } from "@/utils/enum"

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
    cy.window().then(() => {
      const store = useMapStore()
      store.contextData.data = { plantabilityNormalizedIndice: 8.5 }
      store.selectedDataType = DataType.PLANTABILITY
    })
    cy.get('[data-cy="map-context-data"]').should("be.visible")
  })
  it("should hide component when tileDetails is null", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.contextData.data = null
      store.selectedDataType = DataType.PLANTABILITY
    })

    cy.get('[data-cy="map-context-data"]').should("not.exist")
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

    cy.getBySel(`category-${[PlantabilityMetaCategory.BATIMENTS]}`).should("exist")
    cy.getBySel(`"factor-${PlantabilityLandUseKeys.PROXIMITE_FACADE}"`).should("not.exist")
    cy.getBySel(`"factor-${PlantabilityLandUseKeys.BATIMENTS}"`).should("not.exist")

    cy.getBySel(`category-${[PlantabilityMetaCategory.BATIMENTS]}`).click()

    cy.getBySel(`"factor-${PlantabilityLandUseKeys.BATIMENTS}"`).should("exist")
    cy.getBySel(`"factor-${PlantabilityLandUseKeys.PROXIMITE_FACADE}"`).should("exist")
  })
})
