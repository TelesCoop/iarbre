import FeedbackPopin from "@/components/FeedbackPopin.vue"

describe("FeedbackPopin", () => {
  it("correctly send feedback", () => {
    cy.mount(FeedbackPopin, {
      props: {
        modelValue: true
      },
      emits: {
        "submit-feedback": cy.spy().as("submit-feedback")
      }
    })

    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."
    cy.get('input[type="email"]').type(testEmail)
    cy.get("textarea").type(testFeedback)
    cy.getBySel("submit-feedback-button").click()
    cy.get("@submit-feedback").should("have.been.calledWith", {
      email: testEmail,
      feedback: testFeedback
    })
  })
})
