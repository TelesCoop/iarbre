/// <reference types="cypress" />
import ContextDataCompactScore from "@/components/contextData/shared/ContextDataCompactScore.vue"

describe("ContextDataCompactScore", () => {
  it("renders the label and value", () => {
    cy.mount(ContextDataCompactScore, {
      props: {
        label: "Jour",
        value: "7/9"
      }
    })

    cy.get('[data-cy="context-data-score-compact"]').should("exist")
    cy.contains("Jour").should("be.visible")
    cy.contains("7/9").should("be.visible")
  })

  it("applies the provided color to the value", () => {
    cy.mount(ContextDataCompactScore, {
      props: {
        label: "Nuit",
        value: "3/9",
        color: "rgb(255, 0, 0)"
      }
    })

    cy.contains("3/9").should("have.css", "color", "rgb(255, 0, 0)")
  })
})
