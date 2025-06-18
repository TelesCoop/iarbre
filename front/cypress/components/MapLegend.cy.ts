import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import VulnerabilityLegend from "@/components/map/legend/VulnerabilityLegend.vue"
import ClimateZoneLegend from "@/components/map/legend/ClimateZoneLegend.vue"
import { createPinia } from "pinia"

describe("Map legends", () => {
  it("renders correctly plantability legend", () => {
    const pinia = createPinia()
    cy.mount(PlantabilityLegend, {
      global: {
        plugins: [pinia]
      }
    })
    cy.contains(0)
    cy.contains(2)
    cy.contains(4)
    cy.contains(6)
    cy.contains(8)
    cy.contains(10)
    cy.contains("Plantable")
    cy.contains("Non plantable")
  })
  it("renders correctly vulnerability legend", () => {
    const pinia = createPinia()
    cy.mount(VulnerabilityLegend, {
      global: {
        plugins: [pinia]
      }
    })
  })
  it("renders correctly lcz legend", () => {
    const pinia = createPinia()
    cy.mount(ClimateZoneLegend, {
      global: {
        plugins: [pinia]
      }
    })

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
    cy.get('[data-zone="1"]').first().should("have.class", "ring-2")
  })
})
