/// <reference types="cypress" />
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import { PlantabilityLandUseKeys, PlantabilityMetaCategory } from "@/types/plantability"
import { DataType, GeoLevel } from "@/utils/enum"

describe("PlantabilityContextDataList", () => {
  const createMockData = (overrides = {}) => ({
    id: "test-id",
    plantabilityNormalizedIndice: 7.5,
    plantabilityIndice: 7.5,
    details: {
      top5LandUse: {
        [PlantabilityLandUseKeys.PROXIMITE_FACADE]: 85,
        [PlantabilityLandUseKeys.BATIMENTS]: 60,
        [PlantabilityLandUseKeys.VOIRIE]: 45,
        ...overrides
      }
    },
    geolevel: GeoLevel.TILE,
    datatype: DataType.PLANTABILITY,
    iris: 1,
    city: 1
  })

  it("displays empty message when no factors", () => {
    const mockData = {
      id: "test-id",
      plantabilityNormalizedIndice: 7.5,
      plantabilityIndice: 7.5,
      details: "[1, 2, 3, 4, 5]",
      geolevel: GeoLevel.TILE,
      datatype: DataType.PLANTABILITY,
      iris: 1,
      city: 1
    }

    cy.mount(PlantabilityContextDataList, {
      props: {
        data: mockData
      }
    })

    cy.get('[data-cy="empty-message"]').should("exist")
  })

  it("renders plantability list with factors", () => {
    const mockData = createMockData()

    cy.mount(PlantabilityContextDataList, {
      props: {
        data: mockData
      }
    })

    cy.get('[aria-label="Liste des paramètres de plantabilité par catégorie"]').should("exist")
  })

  it("displays category", () => {
    const mockData = createMockData()

    cy.mount(PlantabilityContextDataList, {
      props: {
        data: mockData
      }
    })

    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`).should("exist")
    cy.contains("Bâtiments").should("be.visible")
  })

  it("displays factors within categories", () => {
    const mockData = createMockData({
      [PlantabilityLandUseKeys.BATIMENTS]: 75
    })

    cy.mount(PlantabilityContextDataList, {
      props: {
        data: mockData
      }
    })

    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`).should("exist")
    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`)
      .find(".accordion-header")
      .click()
    cy.contains("Impact").should("be.visible")
    cy.contains("fort").should("be.visible")
  })

  it("handles multiple categories", () => {
    const mockData = createMockData()

    cy.mount(PlantabilityContextDataList, {
      props: {
        data: mockData
      }
    })

    cy.get(`[data-cy="category-${PlantabilityMetaCategory.BATIMENTS}"]`).should("exist")
  })
})
