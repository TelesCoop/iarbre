/// <reference types="cypress" />
import PetContextTool from "@/components/contextTools/PetContextTool.vue"
import { useMapStore } from "@/stores/map"

describe("PetContextTool", () => {
  it("switches the scenario year", () => {
    cy.mount(PetContextTool)
    cy.get('[data-cy="pet-year-2020"]').click()
    cy.get('[data-cy="pet-year-2020"]').should("have.attr", "aria-checked", "true")
    cy.window().then(() => expect(useMapStore().petYear).to.eq(2020))
  })

  it("changes the hour from the slider", () => {
    cy.mount(PetContextTool)
    cy.get('[data-cy="pet-hour-slider"]').invoke("val", 9).trigger("input")
    cy.contains("9h")
    cy.window().should(() => expect(useMapStore().petHour).to.eq(9))
  })
})
