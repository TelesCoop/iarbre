/// <reference types="cypress" />
import MapLayerToggles from "@/components/map/MapLayerToggles.vue"
import { useMapStore } from "@/stores/map"

describe("MapLayerToggles", () => {
  beforeEach(() => {
    cy.mount(MapLayerToggles)
  })

  it("should render the three layer toggle buttons", () => {
    cy.get('[data-cy="qpv-toggle"]').should("be.visible").and("contain.text", "QPV")
    cy.get('[data-cy="cadastre-toggle"]').should("be.visible").and("contain.text", "Cadastre")
    cy.get('[data-cy="boundary-toggle"]').should("be.visible").and("contain.text", "Communes")
  })

  it("should start with all layer toggles inactive", () => {
    cy.get('[data-cy="qpv-toggle"]').should("not.have.class", "active")
    cy.get('[data-cy="cadastre-toggle"]').should("not.have.class", "active")
    cy.get('[data-cy="boundary-toggle"]').should("not.have.class", "active")
  })

  it("should toggle the QPV layer when the QPV button is clicked", () => {
    cy.window().then(() => {
      const store = useMapStore()
      expect(store.showQPVLayer).to.equal(false)
    })

    cy.get('[data-cy="qpv-toggle"]').click()

    cy.window().then(() => {
      const store = useMapStore()
      expect(store.showQPVLayer).to.equal(true)
    })
    cy.get('[data-cy="qpv-toggle"]').should("have.class", "active")
  })

  it("should toggle the cadastre layer when the cadastre button is clicked", () => {
    cy.get('[data-cy="cadastre-toggle"]').click()

    cy.window().then(() => {
      const store = useMapStore()
      expect(store.showCadastreLayer).to.equal(true)
    })
    cy.get('[data-cy="cadastre-toggle"]').should("have.class", "active")
  })

  it("should toggle the boundary layer when the communes button is clicked", () => {
    cy.get('[data-cy="boundary-toggle"]').click()

    cy.window().then(() => {
      const store = useMapStore()
      expect(store.showBoundaryLayer).to.equal(true)
    })
    cy.get('[data-cy="boundary-toggle"]').should("have.class", "active")
  })
})
