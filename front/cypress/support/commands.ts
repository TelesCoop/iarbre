/// <reference types="cypress" />
Cypress.Commands.add("getBySel", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

Cypress.Commands.add("mapOpenPopup", () => {
  cy.getBySel("map-component").should("be.visible").click("center")
  cy.getBySel("score-popup").should("be.visible")
})

Cypress.Commands.add("mapHasNoPopup", () => {
  cy.getBySel("score-popup").should("not.exist")
})

Cypress.Commands.add("mapClosePopup", () => {
  cy.get(".maplibregl-popup-close-button").should("be.visible").click({ force: true })
  cy.mapHasNoPopup()
})

Cypress.Commands.add("mapSwitchLayer", (datatype: string) => {
  cy.getBySel("layer-switcher").should("be.visible").click()
  cy.getBySel("layer-switcher").get(".p-select-option-label").contains(datatype).click()
})

Cypress.Commands.add("basemapSwitchLayer", (maptype: string) => {
  cy.getBySel("map-switcher").should("be.visible").click()
  cy.getBySel("map-switcher").get(".p-select-option-label").contains(maptype).click()
})

Cypress.Commands.add("mapZoomTo", (zoom: number) => {
  for (let i = 1; i < zoom + 1; i++) {
    cy.get(".maplibregl-ctrl-zoom-in").should("be.visible").click()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
  }
})

Cypress.Commands.add("mapCheckQPVLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist ? "cypress: QPV data loaded" : "cypress: QPV data removed"
  cy.window().its("console").invoke("info").should("have.been.calledWith", expectedMessage)
})
