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

    cy.getBySel("submit-feedback-button").click()
    cy.get("@submit-feedback").should("have.been.calledWith", { email: "", feedback: "" })

    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."
    cy.get("textarea").type(testFeedback)
    cy.get('input[type="email"]').type(testEmail)
    cy.getBySel("submit-feedback-button").click()

    // Check if the event was passed with the correct values
    cy.get("@submit-feedback").should("have.been.calledWith", {
      email: testEmail,
      feedback: testFeedback
    })
  })
})
