import FeedbackPopin from "@/components/FeedbackPopin.vue"

describe("Component: FeedbackPopin", () => {
  it("renders correctly", () => {
    cy.mount(FeedbackPopin)

    cy.contains("Votre avis compte !")
    cy.contains("Partagez-nous vos impressions pour nous aider à améliorer le site :")

    cy.get('input[type="email"]').should("exist")
    cy.get("textarea").should("exist")
    cy.get('button[type="submit"]').should("exist")
    cy.get("button.my-popin-close-button").should("exist")
  })
})
