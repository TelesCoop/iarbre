/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Share the current map view", () => {
  beforeEach(() => {
    cy.viewport(1024, 768)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.intercept("POST", "**/api/short-links/", { statusCode: 201, body: { code: "r4Vd9x" } }).as(
      "shortLink"
    )
    cy.visit("/plantability/14/45.75773/4.85377")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("previews, exports and shares the current view", () => {
    cy.getBySel("share-view-button").click()
    cy.getBySel("share-view-dialog").should("be.visible")

    cy.wait("@shortLink")
      .its("request.body")
      .should("deep.equal", { path: "/plantability/14/45.75773/4.85377" })
    cy.getBySel("share-view-short-link").should(
      "have.text",
      `${Cypress.config("baseUrl")}/s/r4Vd9x`
    )

    cy.getBySel("share-view-details")
      .should("contain.text", "Score de plantabilité")
      .and("contain.text", "45.75773° N, 4.85377° E · z14")

    cy.getBySel("share-view-preview").find("img", { timeout: 40000 }).should("be.visible")
    cy.getBySel("share-view-export-button").should("not.be.disabled").click()
    cy.readFile(
      `${Cypress.config("downloadsFolder")}/iarbre_plantability_45.75773_4.85377_z14.png`,
      "binary",
      { timeout: 10000 }
    ).should("have.length.greaterThan", 0)

    cy.getBySel("share-view-width-input").clear()
    cy.getBySel("share-view-width-input").type("400")
    cy.getBySel("share-view-height-input").clear()
    cy.getBySel("share-view-height-input").type("300")
    cy.getBySel("share-view-apply-size-button").should("not.be.disabled").click()
    cy.getBySel("share-view-apply-size-button").should("be.disabled")
    cy.getBySel("share-view-preview").find("img", { timeout: 40000 }).should("be.visible")

    cy.getBySel("share-view-format-select").find(".select-trigger").click()
    cy.getBySel("share-view-format-select").contains(".select-option", "JPEG").click()
    cy.getBySel("share-view-export-button").should("contain.text", "JPEG 400 × 300").click()
    cy.readFile(
      `${Cypress.config("downloadsFolder")}/iarbre_plantability_45.75773_4.85377_z14.jpg`,
      "binary",
      { timeout: 10000 }
    ).should("have.length.greaterThan", 0)

    cy.get(".dialog-close").click()
    cy.getBySel("share-view-dialog").should("not.exist")
  })
})
