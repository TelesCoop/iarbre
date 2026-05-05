/// <reference types="cypress" />
import MapContextDataBiosphereIntegrity from "@/components/contextData/MapContextDataBiosphereIntegrity.vue"
import { DataType, GeoLevel } from "@/utils/enum"
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"

describe("MapContextDataBiosphereIntegrity", () => {
  const mockData: BiosphereIntegrityData = {
    id: "42",
    indice: 67,
    geolevel: GeoLevel.BIOSPHERE_FUNCTIONAL_INTEGRITY,
    datatype: DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY,
    landCovers: [
      { landCover: "feuillu", landCoverLabel: "Feuillu", binary: true, percentage: 45.2 },
      {
        landCover: "zone_impermeable",
        landCoverLabel: "Zone imperméable",
        binary: false,
        percentage: 30.1
      },
      { landCover: "surface_eau", landCoverLabel: "Surface eau", binary: null, percentage: 24.7 }
    ]
  }

  it("displays the circular score and description text", () => {
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: mockData } })
    cy.contains("67").should("be.visible")
    cy.contains("500m").should("be.visible")
  })

  it("shows all land cover entries with labels and percentages", () => {
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: mockData } })
    cy.contains("Couvertures du sol").should("be.visible")
    cy.contains("Feuillu").should("be.visible")
    cy.contains("45.2%").should("be.visible")
    cy.contains("Zone imperméable").should("be.visible")
    cy.contains("30.1%").should("be.visible")
    cy.contains("Surface eau").should("be.visible")
    cy.contains("24.7%").should("be.visible")
  })

  it("shows semi-naturel label when binary is true", () => {
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: mockData } })
    cy.contains("Semi-naturel").should("be.visible")
  })

  it("shows non semi-naturel label when binary is false", () => {
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: mockData } })
    cy.contains("Non semi-naturel").should("be.visible")
  })

  it("hides land cover section when landCovers is null", () => {
    const noLandCoverData: BiosphereIntegrityData = {
      ...mockData,
      landCovers: null
    }
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: noLandCoverData } })
    cy.contains("Couvertures du sol").should("not.exist")
  })

  it("hides land cover section when landCovers is empty", () => {
    const emptyLandCoverData: BiosphereIntegrityData = {
      ...mockData,
      landCovers: []
    }
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: emptyLandCoverData } })
    cy.contains("Couvertures du sol").should("not.exist")
  })

  it("shows empty message when data is null", () => {
    cy.mount(MapContextDataBiosphereIntegrity, { props: { data: null } })
    cy.get('[data-cy="empty-message"]').should("exist")
    cy.contains("Cliquez sur une zone.").should("be.visible")
  })
})
