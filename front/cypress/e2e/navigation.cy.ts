// https://on.cypress.io/api

describe("Navigation", () => {
  it("loads map on root url", () => {
    cy.visit("/")
    cy.getBySel("map-component").should("exist")
    cy.getBySel("navbar").should("exist")
    cy.getBySel("feedback-popin").should("not.exist")
  })
})
