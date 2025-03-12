// https://on.cypress.io/api

describe("Feedback Popin interactivity", () => {
  beforeEach(() => {
    cy.visit("/")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
  })

  it("Open Popin on click", () => {
    cy.contains("button", "✉️ Nous envoyer votre retour").click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("Open, close and reopen feedback popin", () => {
    cy.contains("button", "✉️ Nous envoyer votre retour").click()

    cy.get("button").contains("x").click()
    cy.getBySel("feedback-popin").should("not.exist")

    cy.contains("button", "✉️ Nous envoyer votre retour").click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("Fill and submit the feedback form", () => {
    cy.contains("button", "✉️ Nous envoyer votre retour").click()

    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.get('input[type="email"]').type(testEmail)
    cy.get("textarea").type(testFeedback)

    cy.window().then((win) => {
      cy.stub(win, "fetch").resolves({
        ok: true,
        json: () => Promise.resolve({ message: "Merci pour votre retour !" })
      })
    })

    cy.contains("button", "J'envoie mon avis").click()
    cy.getBySel("feedback-popin").should("not.exist")
  })

  it("Validates required form fields", () => {
    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.contains("button", "✉️ Nous envoyer votre retour").click()

    cy.contains("button", "J'envoie mon avis").click()

    // Shoud still be on the same page
    cy.getBySel("feedback-popin").should("exist")

    // Only email, missing feedback
    cy.get('input[type="email"]').type(testEmail)
    cy.contains("button", "J'envoie mon avis").click()
    cy.getBySel("feedback-popin").should("exist")

    // Should be able to submit without email
    cy.get('input[type="email"]').clear()
    cy.get("textarea").type(testFeedback)
    cy.contains("button", "J'envoie mon avis").click()
    cy.getBySel("feedback-popin").should("not.exist")
  })
})
