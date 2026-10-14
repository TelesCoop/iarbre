/// <reference types="cypress" />
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"

describe("Sidebar", () => {
  beforeEach(() => {
    cy.mount(SidebarComponent)
  })

  it("renders correctly", () => {
    cy.get(".sidebar").should("exist")
    cy.get(".sidebar-logo").should("exist")
    cy.get(".sidebar-icons").should("exist")
  })

  it("has two action buttons", () => {
    cy.get(".sidebar-icon-button").should("have.length", 2)
  })

  it("opens features dialog when features button is clicked", () => {
    cy.get(".sidebar-icon-button").first().click()
    cy.getBySel("welcome-dialog").should("exist")
  })
})
