/// <reference types="cypress" />
import Navbar from "@/components/navbar/NavbarComponent.vue"

describe("Navbar", () => {
  beforeEach(() => {
    cy.mount(Navbar)
  })
  it("renders correctly", () => {
    cy.getBySel("open-feedback-button").should("exist")
  })
  it("fill and submit the feedback form", () => {
    cy.getBySel("open-feedback-button").click()

    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.intercept("POST", "**/feedback/", {
      statusCode: 200,
      body: { message: "Merci pour votre retour !" }
    }).as("submitFeedback")

    cy.get('input[type="email"]').type(testEmail)
    cy.get("textarea").type(testFeedback)
    cy.getBySel("submit-feedback-button").click()

    cy.wait("@submitFeedback").its("response.statusCode").should("eq", 200)

    cy.getBySel("feedback-popin").should("not.exist")
  })
})
