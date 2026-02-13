/// <reference types="cypress" />
import LegalView from "@/views/LegalView.vue"

describe("LegalView", () => {
  beforeEach(() => {
    cy.mount(LegalView, {
      global: {
        stubs: {
          "router-link": {
            template: "<a><slot /></a>"
          }
        }
      }
    })
  })

  it("renders correctly", () => {
    cy.get(".legal-page").should("exist")
    cy.get(".legal-title").should("contain", "Informations légales")
  })

  it("displays legal mentions tab by default", () => {
    cy.get(".legal-tab.active").should("contain", "Mentions légales")
    cy.get(".section-title").should("contain", "Mentions légales")
  })

  it("displays editor information", () => {
    cy.contains("Éditeur du site").should("exist")
    cy.contains("TELESCOOP").should("exist")
    cy.contains("SIREN : 890 488 950").should("exist")
  })

  it("displays host information", () => {
    cy.contains("Hébergeur").should("exist")
    cy.contains("OVH SAS").should("exist")
  })

  it("switches to privacy policy tab", () => {
    cy.contains("button", "Politique de confidentialité").click()
    cy.get(".legal-tab.active").should("contain", "Politique de confidentialité")
    cy.get(".section-title").should("contain", "Politique de confidentialité")
  })

  it("displays GDPR information in privacy tab", () => {
    cy.contains("button", "Politique de confidentialité").click()
    cy.contains("Responsable du traitement").should("exist")
    cy.contains("Données collectées").should("exist")
  })

  it("has working email links", () => {
    cy.get('a[href="mailto:contact@telescoop.fr"]').should("exist")
  })

  it("has working external links", () => {
    cy.get('a[href="https://www.ovhcloud.com"]').should("have.attr", "target", "_blank")
    cy.get('a[href="https://www.ovhcloud.com"]').should("have.attr", "rel", "noopener noreferrer")
  })

  it("has a back button to return to the map", () => {
    cy.contains("button", "Retour à la carte").should("exist")
  })

  it("displays legal icon", () => {
    cy.get(".legal-title-block svg").should("exist")
  })
})
