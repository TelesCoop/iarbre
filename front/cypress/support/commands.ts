/// <reference types="cypress" />

/**
 * Custom command to get element by data-cy attribute
 */
Cypress.Commands.add("getBySel", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

/**
 * Custom command to switch data layer on desktop (via sidebar)
 * @deprecated Use direct selectors in tests for better clarity
 */
Cypress.Commands.add("mapSwitchLayer", (datatype: string) => {
  cy.getBySel("layer-switcher").filter(":visible").first().should("be.visible").click()
  cy.get(".p-select-option-label").contains(datatype).click()
})

/**
 * Custom command to switch basemap style on desktop (via background selector)
 * @deprecated Use direct selectors in tests for better clarity
 */
Cypress.Commands.add("basemapSwitchLayer", (maptype: string) => {
  cy.getBySel("bg-selector-toggle").filter(":visible").first().should("be.visible").click()
  cy.get(`[data-cy="bg-option-${maptype}"]`).should("be.visible").click()
})

/**
 * Custom command to zoom in on map
 */
Cypress.Commands.add("mapZoomTo", (zoom: number) => {
  for (let i = 1; i < zoom + 1; i++) {
    cy.get(".maplibregl-ctrl-zoom-in").should("be.visible").click()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
  }
})

/**
 * Custom command to check QPV layer status via console logs
 */
Cypress.Commands.add("mapCheckQPVLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist ? "cypress: QPV data loaded" : "cypress: QPV data removed"
  cy.get("@consoleInfo").should("have.been.calledWith", expectedMessage)
})

/**
 * Custom command to check cadastre layer status via console logs
 */
Cypress.Commands.add("mapCheckCadastreLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist
    ? "cypress: cadastre data loaded"
    : "cypress: cadastre data removed"
  cy.get("@consoleInfo").should("have.been.calledWith", expectedMessage)
})
