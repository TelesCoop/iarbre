/// <reference types="cypress" />
import { h } from "vue"
import DashboardFooter from "@/components/dashboard/DashboardFooter.vue"
import AppToast from "@/components/shared/AppToast.vue"

const WrapperWithToast = {
  render() {
    return h("div", [h(DashboardFooter), h(AppToast, { group: "br" })])
  }
}

describe("DashboardFooter export", () => {
  it("downloads a PDF and shows a success toast", () => {
    cy.intercept("POST", "**/dashboard/export-pdf/", {
      statusCode: 200,
      headers: { "content-type": "application/pdf" },
      body: "%PDF-1.7 fake"
    }).as("export")

    cy.stub(window.URL, "createObjectURL").returns("blob:stub")
    cy.stub(window.URL, "revokeObjectURL")

    cy.mount(WrapperWithToast)
    cy.contains("Télécharger").click()
    cy.wait("@export")
    cy.contains("Rapport généré").should("exist")
  })

  it("shows an error toast on server error", () => {
    cy.intercept("POST", "**/dashboard/export-pdf/", { statusCode: 504 }).as("export")

    cy.mount(WrapperWithToast)
    cy.contains("Télécharger").click()
    cy.wait("@export")
    cy.contains("échoué").should("exist")
  })
})
