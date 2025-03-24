// https://on.cypress.io/api

describe("Map interactivity", () => {
  beforeEach(() => {
    cy.visit("/")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("Map loading seems to be okay", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })
  it.skip("Open popup on click", () => {
    cy.openPopup()
  })

  it.skip("Open, close and reopen popup. Resolve #92", () => {
    cy.openPopup()
    cy.closePopup()
    cy.openPopup()
  })

  it.skip("Open popup, close it, switch layer and reopen popup. Resolve #142", () => {
    cy.openPopup()
    cy.closePopup()
    cy.switchLayer("lcz")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.openPopup()
  })
})
