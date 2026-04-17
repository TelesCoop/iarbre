import MapSidePanelDownload from "@/components/map/panels/sidepanel/MapSidePanelDownload.vue"

describe("MapSidePanelDownload", () => {
  beforeEach(() => {
    cy.mount(MapSidePanelDownload)
  })

  it("should render the button with correct content", () => {
    cy.contains("Collectivités, aménageurs, urbanistes").should("be.visible")
    cy.get('[data-cy="api-doc"]').should("be.visible")
    cy.contains("Obtenir les données").should("be.visible")
    cy.get('[data-cy="api-doc"] svg path').should("have.attr", "stroke", "#426A45")
  })

  it("should not show the dialog initially", () => {
    cy.contains("Export des données").should("not.exist")
  })

  it("should open the API doc dialog when button is clicked", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("Export des données").should("be.visible")
  })

  it("should show WFS and raster sections in the dialog", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("WEB FEATURE SERVICE").should("be.visible")
    cy.contains("REST - GeoTIFF").should("be.visible")
  })

  it("should expand WFS section and show params table and URL", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("WEB FEATURE SERVICE").click()
    cy.contains("PARAMÈTRES").should("be.visible").click()
    cy.contains("TYPENAMES").should("be.visible")
    cy.contains("OUTPUTFORMAT").should("be.visible")
    cy.contains(`${window.location.origin}/api/wfs/`).should("be.visible")
  })

  it("should expand raster section and show dataset URLs", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("REST - GeoTIFF").click()
    cy.contains("Plantabilité").should("be.visible")
    cy.contains("Végéstrate").should("be.visible")
    cy.contains(`${window.location.origin}/api/rasters/plantability`).should("be.visible")
    cy.contains(`${window.location.origin}/api/rasters/vegestrate`).should("be.visible")
  })

  it("should close the dialog when close button is clicked", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("Export des données").should("be.visible")
    cy.get('[aria-label="Fermer"]').click()
    cy.contains("Export des données").should("not.exist")
  })
})
