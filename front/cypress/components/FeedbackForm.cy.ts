import FeedbackForm from "@/components/forms/FeedbackForm.vue"
import Button from "primevue/button"
import InputText from "primevue/inputtext"
import Textarea from "primevue/textarea"

describe("FeedbackForm.vue", () => {
  beforeEach(() => {
    cy.mount(FeedbackForm, {
      global: {
        components: {
          Button,
          InputText,
          Textarea
        }
      }
    })
  })

  it("renders the form with all elements", () => {
    cy.contains("Partagez-nous vos impressions").should("be.visible")
    cy.get('input[type="email"]').should("be.visible")
    cy.get("textarea").should("be.visible")
    cy.get('[data-cy="submit-feedback-button"]').should("be.visible")
  })

  it("allows entering email and feedback", () => {
    cy.get('input[type="email"]').type("test@example.com")
    cy.get('input[type="email"]').should("have.value", "test@example.com")

    cy.get("textarea").type("This is my feedback")
    cy.get("textarea").should("have.value", "This is my feedback")
  })

  it("emits submit-feedback event on form submission", () => {
    const onSubmitSpy = cy.spy().as("submitSpy")

    cy.mount(FeedbackForm, {
      global: {
        components: {
          Button,
          InputText,
          Textarea
        }
      },
      props: {
        onSubmitFeedback: onSubmitSpy
      }
    })

    cy.get('input[type="email"]').type("user@test.com")
    cy.get("textarea").type("Great app!")
    cy.get('[data-cy="submit-feedback-button"]').click()

    cy.get("@submitSpy").should("have.been.calledWith", {
      email: "user@test.com",
      feedback: "Great app!"
    })
  })

  it("accepts initial email and feedback props", () => {
    cy.mount(FeedbackForm, {
      global: {
        components: {
          Button,
          InputText,
          Textarea
        }
      },
      props: {
        email: "initial@example.com",
        feedback: "Initial feedback"
      }
    })

    cy.get('input[type="email"]').should("have.value", "initial@example.com")
    cy.get("textarea").should("have.value", "Initial feedback")
  })

  it("prevents default form submission behavior", () => {
    cy.mount(FeedbackForm, {
      global: {
        components: {
          Button,
          InputText,
          Textarea
        }
      }
    })

    cy.get("textarea").type("Test message")
    cy.get("form").then(($form) => {
      $form.on("submit", (e) => {
        expect(e.isDefaultPrevented()).to.be.true
      })
    })
    cy.get('[data-cy="submit-feedback-button"]').click()
  })
})
