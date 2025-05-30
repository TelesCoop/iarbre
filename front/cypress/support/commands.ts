/// <reference types="cypress" />
Cypress.Commands.add("getBySel", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

Cypress.Commands.add("mapOpenPopup", () => {
  cy.getBySel("map-component").click("center")
  cy.getBySel("score-popup").should("be.visible")
})

Cypress.Commands.add("mapHasNoPopup", () => {
  cy.getBySel("score-popup").should("not.exist")
})

Cypress.Commands.add("mapClosePopup", () => {
  cy.get(".maplibregl-popup-close-button").click({ force: true })
  cy.mapHasNoPopup()
})

Cypress.Commands.add("mapSwitchLayer", (datatype: string) => {
  cy.getBySel("layer-switcher").click()
  cy.getBySel("layer-switcher").get(".p-select-option-label").contains(datatype).click()
})

Cypress.Commands.add("basemapSwitchLayer", (maptype: string) => {
  cy.getBySel("map-switcher").click()
  cy.getBySel("map-switcher").get(".p-select-option-label").contains(maptype).click()
})
