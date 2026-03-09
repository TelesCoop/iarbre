import MapSidePanel from "@/components/map/panels/sidepanel/MapSidePanel.vue"

describe("MapSidePanel", () => {
  beforeEach(() => {
    cy.mount(MapSidePanel)
  })

  it("should include all sub-components", () => {
    cy.get('[data-cy="map-side-panel-header"]').should("exist")
    cy.contains("QPV").should("be.visible")
    cy.contains("Cadastre").should("be.visible")
    cy.get('[data-cy="map-layer-switcher"]').should("exist")
    cy.get('[data-cy="map-context-data"]').should("exist")
    cy.get('[data-cy="map-side-panel-download"]').should("exist")
    cy.get('[data-cy="map-side-panel-footer"]').should("exist")
  })
})
