/// <reference types="cypress" />

describe("Welcome message feedback button", () => {
  it("opens feedback popin when clicking 'Donnez votre avis' in welcome dialog", () => {
    cy.visit("/")

    // Welcome dialog should be visible for first-time visitors
    cy.getBySel("welcome-dialog").should("exist")

    // Click the feedback button in the welcome dialog
    cy.getBySel("welcome-feedback-tutorial").click()

    // Welcome dialog should close
    cy.getBySel("welcome-dialog").should("not.exist")

    // Feedback popin should open
    cy.getBySel("feedback-popin").should("exist")
  })
})
