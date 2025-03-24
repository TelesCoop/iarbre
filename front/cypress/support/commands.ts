/// <reference types="cypress" />
Cypress.Commands.add("getBySel", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

Cypress.Commands.add("openPopup", () => {
  cy.getBySel("map-component").click("center")
  cy.getBySel("score-popup").should("be.visible")
})

Cypress.Commands.add("closePopup", () => {
  cy.get(".maplibregl-popup-close-button").click({ force: true })
  cy.getBySel("score-popup").should("not.exist")
})

Cypress.Commands.add("switchLayer", (datatype: string) => {
  cy.getBySel("layer-switcher").get("select").select(datatype)
})
