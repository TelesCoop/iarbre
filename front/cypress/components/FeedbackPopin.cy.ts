import FeedbackPopin from "@/components/FeedbackPopin.vue"

describe("Component: FeedbackPopin", () => {
  it("renders correctly", () => {
    cy.mount(FeedbackPopin)
    cy.getBySel("submit-feedback-button").should("exist")
    cy.getBySel("close-feedback-button").should("exist")
  })
})
