/// <reference types="cypress" />
import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import { PlantabilityLandUseKeys, PlantabilityMetaCategory } from "@/types/plantability"
import { DataType } from "@/utils/enum"

describe("PlantabilityContextDataList", () => {
  it("renders empty state when no data", () => {
    const pinia = createPinia()

    mount(PlantabilityContextDataList, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: null
      }
    })

    cy.contains("Aucune donnée disponible")
  })

  it("renders plantability categories", () => {
    const pinia = createPinia()
    const mockData = {
      plantabilityNormalizedIndice: 7.5,
      details: {
        top5LandUse: {
          [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 85,
          [PlantabilityLandUseKeys.BATIMENTS]: 60,
          [PlantabilityLandUseKeys.VOIRIE]: 45
        }
      },
      datatype: DataType.PLANTABILITY
    }

    mount(PlantabilityContextDataList, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel(`category-${PlantabilityMetaCategory.BATIMENTS}`).should("exist")
    cy.getBySel(`category-${PlantabilityMetaCategory.VOIRIE}`).should("exist")
  })

  it("expands category on click", () => {
    const pinia = createPinia()
    const mockData = {
      plantabilityNormalizedIndice: 7.5,
      details: {
        top5LandUse: {
          [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 85,
          [PlantabilityLandUseKeys.BATIMENTS]: 60
        }
      },
      datatype: DataType.PLANTABILITY
    }

    mount(PlantabilityContextDataList, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel(`category-${PlantabilityMetaCategory.BATIMENTS}`).click()
    cy.getBySel(`factor-${PlantabilityLandUseKeys.BATIMENTS}`).should("exist")
    cy.getBySel(`factor-${PlantabilityLandUseKeys.PROXIMITE_FACADE}`).should("exist")
  })

  it("collapses category on second click", () => {
    const pinia = createPinia()
    const mockData = {
      plantabilityNormalizedIndice: 7.5,
      details: {
        top5LandUse: {
          [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 85,
          [PlantabilityLandUseKeys.BATIMENTS]: 60
        }
      },
      datatype: DataType.PLANTABILITY
    }

    mount(PlantabilityContextDataList, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel(`category-${PlantabilityMetaCategory.BATIMENTS}`).click()
    cy.getBySel(`factor-${PlantabilityLandUseKeys.BATIMENTS}`).should("exist")

    cy.getBySel(`category-${PlantabilityMetaCategory.BATIMENTS}`).click()
    cy.getBySel(`factor-${PlantabilityLandUseKeys.BATIMENTS}`).should("not.exist")
  })

  it("displays correct values for factors", () => {
    const pinia = createPinia()
    const mockData = {
      plantabilityNormalizedIndice: 7.5,
      details: {
        top5LandUse: {
          [PlantabilityLandUseKeys.BATIMENTS]: 60
        }
      },
      datatype: DataType.PLANTABILITY
    }

    mount(PlantabilityContextDataList, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel(`category-${PlantabilityMetaCategory.BATIMENTS}`).click()
    cy.getBySel(`factor-${PlantabilityLandUseKeys.BATIMENTS}`).should("contain", "60")
  })
})
