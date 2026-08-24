/// <reference types="cypress" />
import ContextDataZoomHint from "@/components/contextData/shared/ContextDataZoomHint.vue"
import { useMapStore } from "@/stores/map"

describe("ContextDataZoomHint", () => {
  it("renders a zoom-in hint and zooms to the target on click", () => {
    cy.mount(ContextDataZoomHint, {
      props: {
        direction: "in",
        message: "Zoomez pour le détail",
        targetZoom: 17
      }
    })

    cy.get('[data-cy="zoom-hint"]').should("exist")
    cy.get('[data-cy="zoom-hint-button"]').should("contain.text", "Zoomer")

    cy.window().then(() => {
      cy.stub(useMapStore(), "zoomTo").as("zoomTo")
    })
    cy.get('[data-cy="zoom-hint-button"]').click()
    cy.get("@zoomTo").should("have.been.calledWith", 17)
  })

  it("renders a zoom-out hint and zooms to the target on click", () => {
    cy.mount(ContextDataZoomHint, {
      props: {
        direction: "out",
        message: "Dézoomez pour la distribution",
        targetZoom: 15
      }
    })

    cy.get('[data-cy="zoom-out-hint"]').should("exist")
    cy.get('[data-cy="zoom-out-hint-button"]').should("contain.text", "Dézoomer")

    cy.window().then(() => {
      cy.stub(useMapStore(), "zoomTo").as("zoomTo")
    })
    cy.get('[data-cy="zoom-out-hint-button"]').click()
    cy.get("@zoomTo").should("have.been.calledWith", 15)
  })
})
