/// <reference types="cypress" />
import MapContextData from "@/components/contextData/MapContextData.vue"
import { useMapStore } from "@/stores/map"

describe("MapContextData states", () => {
  it("shows a loading skeleton while calculating", () => {
    cy.mount(MapContextData)

    cy.window().then(() => {
      useMapStore().isCalculating = true
    })

    cy.get('[data-cy="context-data-skeleton"]').should("exist")
  })

  it("shows an error state with a retry action when the fetch failed", () => {
    cy.mount(MapContextData)

    cy.window().then(() => {
      const store = useMapStore()
      store.isCalculating = false
      store.contextData.error = true
      cy.stub(store.contextData, "retry").as("retry")
    })

    cy.get('[data-cy="context-data-error"]').should("be.visible")
    cy.get('[data-cy="context-data-retry"]').click()
    cy.get("@retry").should("have.been.called")
  })
})
