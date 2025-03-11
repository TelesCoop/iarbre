import Navbar from "@/components/NavbarComponent.vue"

describe("Component:Navbar", () => {
  it("renders correctly", () => {
    cy.mount(Navbar)
    cy.contains("✉️ Nous envoyer votre retour")
    cy.contains("ⓘ En savoir plus")
  })
})
