// https://on.cypress.io/api

describe("Map interactivity", () => {
  beforeEach(() => {
    cy.visit("/")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
  })

  it("Map loading seems to be okay", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })
  it.only("Opens popup on click", () => {
    cy.getBySel("map-component").click("center")
    cy.getBySel("score-popup").should("be.visible")
  })
})
