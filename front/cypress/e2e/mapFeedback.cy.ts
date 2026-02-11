/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Map feedback", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/")
  })

  it("Open Popin on click", () => {
    cy.get(".sidebar-icon-button").first().click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("Open, close and reopen feedback popin", () => {
    cy.get(".sidebar-icon-button").first().click()

    cy.get(".dialog-close").click()
    cy.getBySel("feedback-popin").should("not.exist")

    cy.get(".sidebar-icon-button").first().click()
    cy.getBySel("feedback-popin").should("exist")
  })
})
