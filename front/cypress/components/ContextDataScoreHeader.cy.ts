/// <reference types="cypress" />
import ContextDataScoreHeader from "@/components/contextData/shared/ContextDataScoreHeader.vue"

describe("ContextDataScoreHeader", () => {
  it("renders the swatch label, eyebrow and title", () => {
    cy.mount(ContextDataScoreHeader, {
      props: {
        swatchLabel: "A",
        swatchColor: "#426a45",
        eyebrow: "Zone climatique locale",
        title: "Bâti compact de faible hauteur"
      }
    })

    cy.contains("A").should("be.visible")
    cy.contains("Zone climatique locale").should("be.visible")
    cy.contains("Bâti compact de faible hauteur").should("be.visible")
  })

  it("applies the swatch background color", () => {
    cy.mount(ContextDataScoreHeader, {
      props: {
        swatchLabel: "62%",
        swatchColor: "rgb(66, 106, 69)",
        eyebrow: "Intégrité fonctionnelle",
        title: "Espace semi-naturel"
      }
    })

    cy.get(".score-header-swatch").should("have.attr", "style").and("include", "background-color")
  })
})
