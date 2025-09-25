/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Map feedback", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/")
  })

  it("Open Popin on click", () => {
    cy.getBySel("open-feedback-button").click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("Open, close and reopen feedback popin", () => {
    cy.getBySel("open-feedback-button").click()

    cy.get("[data-pc-name='pcclosebutton']").click()
    cy.getBySel("feedback-popin").should("not.exist")

    cy.getBySel("open-feedback-button").click()
    cy.getBySel("feedback-popin").should("exist")
  })
})
