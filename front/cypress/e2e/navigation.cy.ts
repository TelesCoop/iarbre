/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Navigation", () => {
  it("loads map on root url", () => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/")
    cy.visit("/")
    cy.getBySel("map-component").should("exist")
    cy.get(".sidebar").should("exist")
    cy.getBySel("feedback-popin").should("not.exist")
  })
})
