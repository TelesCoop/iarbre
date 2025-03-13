import FeedbackPopin from "@/components/FeedbackPopin.vue"

describe("Component: FeedbackPopin", () => {
  it("renders correctly", () => {
    cy.mount(FeedbackPopin)
    cy.getBySel("submit-feedback-button").should("exist")
    cy.getBySel("close-feedback-button").should("exist")
  })

  it("correctly send feedback", () => {
    cy.mount(FeedbackPopin, {
      props: {
        allowedExtensions: []
      },
      emits: {
        "submit-feedback": cy.spy().as("submit-feedback")
      }
    })
    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.getBySel("submit-feedback-button").click()

    // Should still be on the same page
    cy.get("@submit-feedback").should("not.have.been.called")

    // Only email, missing feedback
    cy.get('input[type="email"]').type(testEmail)
    cy.getBySel("submit-feedback-button").click()
    cy.get("@submit-feedback").should("not.have.been.called")

    // Should be able to submit without email
    // cy.get('input[type="email"]').clear()
    cy.get("textarea").type(testFeedback)
    cy.getBySel("submit-feedback-button").click()
    cy.get("@submit-feedback").should("have.been.called")

    // Check if the event was passed with the correct values
    cy.get("@submit-feedback").should("have.been.calledWith", {
      email: testEmail,
      feedback: testFeedback
    })
  })
})
