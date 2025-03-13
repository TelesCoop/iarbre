// https://on.cypress.io/api

describe("Feedback Popin interactivity", () => {
  beforeEach(() => {
    cy.visit("/")
  })

  it("Open Popin on click", () => {
    cy.getBySel("open-feedback-button").click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("Open, close and reopen feedback popin", () => {
    cy.getBySel("open-feedback-button").click()

    cy.getBySel("close-feedback-button").click()
    cy.getBySel("feedback-popin").should("not.exist")

    cy.getBySel("open-feedback-button").click()
    cy.getBySel("feedback-popin").should("exist")
  })
  it("Validates required form fields", () => {
    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.getBySel("open-feedback-button").click()

    cy.getBySel("submit-feedback-button").click()

    // Shoud still be on the same page
    cy.getBySel("feedback-popin").should("exist")

    // Only email, missing feedback
    cy.get('input[type="email"]').type(testEmail)
    cy.getBySel("submit-feedback-button").click()
    cy.getBySel("feedback-popin").should("exist")

    // Should be able to submit without email
    cy.get('input[type="email"]').clear()
    cy.get("textarea").type(testFeedback)
    cy.getBySel("submit-feedback-button").click()
    cy.getBySel("feedback-popin").should("not.exist")
  })
})
