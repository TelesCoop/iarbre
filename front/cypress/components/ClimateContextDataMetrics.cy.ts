/// <reference types="cypress" />
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import { ClimateDataDetailsKey } from "@/types/climate"
import { DataType, GeoLevel } from "@/utils/enum"

describe("ClimateContextDataMetrics", () => {
  const createMockData = (overrides = {}) => ({
    details: {
      [ClimateDataDetailsKey.HRE]: 12.5,
      [ClimateDataDetailsKey.ARE]: 150,
      [ClimateDataDetailsKey.BUR]: 35,
      [ClimateDataDetailsKey.ROR]: 25,
      [ClimateDataDetailsKey.BSR]: 10,
      [ClimateDataDetailsKey.WAR]: 5,
      [ClimateDataDetailsKey.VER]: 25,
      [ClimateDataDetailsKey.VHR]: 60,
      ...overrides
    },
    datatype: DataType.CLIMATE,
    geolevel: GeoLevel.TILE,
    id: 1,
    geometry: "POINT(0 0)",
    mapGeometry: "POINT(0 0)",
    lczIndex: "LCZ 5",
    lczDescription: "Zone urbaine ouverte"
  })

  it("renders with climate data", () => {
    const mockData = createMockData()

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.get('[aria-label="Liste des indicateurs climatiques par catégorie"]').should("exist")
  })

  it("displays building characteristics", () => {
    const mockData = createMockData({
      [ClimateDataDetailsKey.HRE]: 18.5,
      [ClimateDataDetailsKey.ARE]: 200
    })

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.contains("Caractéristiques du bâti").should("exist")
  })

  it("displays surface types", () => {
    const mockData = createMockData({
      [ClimateDataDetailsKey.BUR]: 40,
      [ClimateDataDetailsKey.ROR]: 30
    })

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.contains("Types de surfaces").should("exist")
  })

  it("displays vegetation and water metrics", () => {
    const mockData = createMockData({
      [ClimateDataDetailsKey.VER]: 35,
      [ClimateDataDetailsKey.WAR]: 8
    })

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.contains("Végétation et eau").should("exist")
  })

  it("handles categories expansion", () => {
    const mockData = createMockData()

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.get('[data-cy="category-building"]').click()
    cy.contains("12.5").should("be.visible")
  })

  it("displays all climate metrics", () => {
    const mockData = createMockData()

    cy.mount(ClimateContextDataMetrics, {
      props: {
        data: mockData
      }
    })

    cy.get('[aria-label="Liste des indicateurs climatiques par catégorie"]').should("exist")
  })
})
