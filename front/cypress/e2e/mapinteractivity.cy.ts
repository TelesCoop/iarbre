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
  it.skip("Open popup on click", () => {
    cy.getBySel("map-component").click("center")
    cy.getBySel("score-popup").should("be.visible")
  })

  it.skip("Open, case and reopen popup. Resolve #92", () => {
    cy.getBySel("map-component").click("center")
    cy.getBySel("score-popup").should("be.visible")

    // This might be behind the legend
    cy.get(".maplibregl-popup-close-button").click({ force: true })
    cy.getBySel("score-popup").should("not.exist")

    cy.getBySel("map-component").click("center")
    cy.getBySel("score-popup").should("be.visible")
  })
})
