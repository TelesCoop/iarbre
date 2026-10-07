import MapSidePanelDownload from "@/components/map/panels/sidepanel/MapSidePanelDownload.vue"
import { RASTER_LAYERS } from "@/utils/rasterLayers"

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

  it("should show WMS and raster sections in the dialog", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("WEB MAP SERVICE").should("be.visible")
    cy.contains("Téléchargement direct des rasters").should("be.visible")
  })

  it("should expand raster section and show dataset URLs", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("Téléchargement direct des rasters").click()
    RASTER_LAYERS.forEach((layer) => cy.contains(layer.label).should("be.visible"))
  })

  it("should close the dialog when close button is clicked", () => {
    cy.get('[data-cy="api-doc"]').click()
    cy.contains("Export des données").should("be.visible")
    cy.get('[aria-label="Fermer"]').click()
    cy.contains("Export des données").should("not.exist")
  })
})
