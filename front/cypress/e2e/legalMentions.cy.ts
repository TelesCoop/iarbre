/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Legal Mentions Navigation", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
  })

  it("navigates to legal mentions page", () => {
    cy.visit("/mentions-legales")
    cy.get(".legal-page").should("exist")
    cy.get(".legal-title").should("contain", "Informations légales")
  })

  it("navigates back to map from legal page", () => {
    cy.visit("/mentions-legales")
    cy.contains("button", "Retour à la carte").click()
    cy.url().should("eq", Cypress.config().baseUrl + "/")
    cy.getBySel("map-component").should("exist")
  })

  it("legal mentions link opens in new tab from feedback form", () => {
    cy.visit("/")
    cy.get(".sidebar-icon-button").first().click()
    cy.get('a[href="/mentions-legales"]').should("have.attr", "target", "_blank")
  })

  it("legal mentions link exists in welcome message", () => {
    LocalStorageHandler.removeItem("hasVisitedBefore")
    cy.visit("/")
    cy.get('a[href="/mentions-legales"]').should("exist")
  })
})
