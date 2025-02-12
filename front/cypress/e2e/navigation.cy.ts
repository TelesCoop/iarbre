// https://on.cypress.io/api

describe("Navigation", () => {
  it("loads map on root url", () => {
    cy.visit("/")
    cy.getBySel("map-component").should("exist")
  })
})
