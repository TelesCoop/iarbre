/// <reference types="cypress" />
import ContextDataSkeleton from "@/components/contextData/shared/ContextDataSkeleton.vue"

describe("ContextDataSkeleton", () => {
  it("renders the default number of skeleton rows", () => {
    cy.mount(ContextDataSkeleton)

    cy.get('[data-cy="context-data-skeleton"]').should("exist")
    cy.get(".skeleton-row").should("have.length", 4)
  })

  it("respects the rows prop", () => {
    cy.mount(ContextDataSkeleton, { props: { rows: 6 } })

    cy.get(".skeleton-row").should("have.length", 6)
  })
})
