/// <reference types="cypress" />
import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import VulnerabilityLegend from "@/components/map/legend/VulnerabilityLegend.vue"
import ClimateZoneLegend from "@/components/map/legend/ClimateZoneLegend.vue"

describe("Map legends", () => {
  it("renders correctly plantability legend", () => {
    cy.mount(PlantabilityLegend)
    cy.contains("Plantable")
    cy.contains("Non plantable")
  })

  it("renders correctly vulnerability legend", () => {
    cy.mount(VulnerabilityLegend)
  })

  it("renders correctly lcz legend", () => {
    cy.mount(ClimateZoneLegend)

    cy.get('[data-cy="climate-zones-legend"]').should("be.visible")

    // Test zone indicators are present
    cy.get('[data-zone="1"]').should("be.visible")
    cy.get('[data-zone="A"]').should("be.visible")
    cy.get('[data-zone="G"]').should("be.visible")

    // Test expand/collapse functionality
    cy.contains("Afficher les détails").should("be.visible")
    cy.contains("Afficher les détails").click()
    cy.contains("Masquer les détails").should("be.visible")

    // Test that detailed view shows zone descriptions
    cy.contains("LCZ 1 :").should("be.visible")
    cy.contains("LCZ A :").should("be.visible")

    // Test zone clicking for filter toggle
    cy.get('[data-zone="1"]').first().click()
    cy.get('[data-zone="1"]').first().should("have.class", "border-2")
  })
})
