/// <reference types="cypress" />
import { createRouter, createMemoryHistory } from "vue-router"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: "/", name: "map", component: { template: "<div />" } },
    { path: "/dashboard", name: "dashboard", component: { template: "<div />" } }
  ]
})

describe("Sidebar", () => {
  beforeEach(() => {
    cy.mount(SidebarComponent, {
      global: {
        plugins: [router]
      }
    })
  })

  it("renders correctly", () => {
    cy.get(".sidebar").should("exist")
    cy.get(".sidebar-logo").should("exist")
    cy.get(".sidebar-icons").should("exist")
  })

  it("has three action buttons", () => {
    cy.get(".sidebar-icon-button").should("have.length", 3)
  })

  it("opens feedback form when contact button is clicked", () => {
    cy.get(".sidebar-icon-button").first().click()
    cy.getBySel("feedback-popin").should("exist")
  })

  it("opens features dialog when features button is clicked", () => {
    cy.get(".sidebar-icon-button").eq(1).click()
    cy.getBySel("welcome-dialog").should("exist")
  })

  it("fill and submit the feedback form", () => {
    cy.get(".sidebar-icon-button").first().click()

    const testEmail = "molly.maguire@test.fr"
    const testFeedback = "Raise the floor, not just the ceiling."

    cy.intercept("POST", "**/feedback/", {
      statusCode: 200,
      body: { message: "Merci pour votre retour !" }
    }).as("submitFeedback")

    cy.get('input[type="email"]').type(testEmail)
    cy.get("textarea").type(testFeedback)
    cy.get(".consent-checkbox").check()
    cy.getBySel("submit-feedback-button").click()

    cy.wait("@submitFeedback").its("response.statusCode").should("eq", 200)

    cy.getBySel("feedback-popin").should("not.exist")
  })
})
