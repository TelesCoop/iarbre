/// <reference types="cypress" />
import MapLegend from "@/components/map/legend/MapLegend.vue"
import { RASTER_LAYERS } from "@/utils/rasterLayers"

describe("MapLegend", () => {
  it("renders the selected raster legend", () => {
    cy.mount(MapLegend)
    cy.getBySel("raster-legend").children().should("have.length", RASTER_LAYERS[0].legend.length)
    cy.contains(RASTER_LAYERS[0].legend[0].label)
  })
})
