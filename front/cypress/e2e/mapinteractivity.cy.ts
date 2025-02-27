// https://on.cypress.io/api

describe("Map interactivity", () => {
  beforeEach(() => {
    cy.visit("/")
  })

  it("Map loading seems to be okay", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })
  it.only("Opens popup on click", () => {
    // eslint-disable-next-line
    cy.wait(4000)
    cy.getBySel("map-component").click("center")
    cy.getBySel("score-popup").should("be.visible")
  })
})
