/// <reference types="cypress" />
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import { PlantabilityLandUseKeys, PlantabilityMetaCategory } from "@/types/plantability"
import { DataType, GeoLevel } from "@/utils/enum"
import { useMapStore } from "@/stores/map"

describe("PlantabilityContextDataList", () => {
  const distributionMockData = {
    id: "test-id",
    plantabilityNormalizedIndice: 7.5,
    plantabilityIndice: 7.5,
    details: "[1, 2, 3, 4, 5]",
    geolevel: GeoLevel.TILE,
    datatype: DataType.PLANTABILITY,
    iris: 1,
    city: 1
  }

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

  it("shows the zoom hint when only the score distribution is available", () => {
    cy.mount(PlantabilityContextDataList, {
      props: {
        data: distributionMockData
      }
    })

    cy.get('[data-cy="zoom-hint"]').should("exist")
    cy.get('[data-cy="zoom-hint-button"]').should("exist")
  })

  it("zooms in to the land-use detail level when clicking the zoom hint button", () => {
    cy.mount(PlantabilityContextDataList, {
      props: {
        data: distributionMockData
      }
    })

    cy.window().then(() => {
      cy.stub(useMapStore(), "zoomTo").as("zoomTo")
    })

    cy.get('[data-cy="zoom-hint-button"]').click()
    cy.get("@zoomTo").should("have.been.calledWith", 17)
  })

  it("shows the zoom-out hint when the land-use detail is displayed", () => {
    cy.mount(PlantabilityContextDataList, {
      props: {
        data: createMockData()
      }
    })

    cy.get('[data-cy="zoom-out-hint"]').should("exist")
    cy.get('[data-cy="zoom-out-hint-button"]').should("exist")
  })

  it("zooms out to the score distribution level when clicking the zoom-out hint button", () => {
    cy.mount(PlantabilityContextDataList, {
      props: {
        data: createMockData()
      }
    })

    cy.window().then(() => {
      cy.stub(useMapStore(), "zoomTo").as("zoomTo")
    })

    cy.get('[data-cy="zoom-out-hint-button"]').click()
    cy.get("@zoomTo").should("have.been.calledWith", 15)
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
