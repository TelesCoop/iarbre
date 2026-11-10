/// <reference types="cypress" />
import PlantabilityContextDataLimits from "@/components/contextData/plantability/PlantabilityContextDataLimits.vue"

describe("PlantabilityContextDataLimits", () => {
  it("expands to show the limits on click", () => {
    cy.mount(PlantabilityContextDataLimits)

    cy.contains("Limites du score").should("be.visible")
    cy.contains("Parkings souterrains").should("not.be.visible")

    cy.get('[data-cy="plantability-limits-toggle"]').click()
    cy.contains("Parkings souterrains").should("be.visible")
    cy.contains("Domaine privé").should("be.visible")
  })
})
