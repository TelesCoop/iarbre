/// <reference types="cypress" />
import { RASTER_LAYERS } from "../../src/utils/rasterLayers"

const API_URL = `${Cypress.config("baseUrl")}/api`
const MAP_POSITION = "13/45.76000/4.85000"

describe("API", () => {
  it("health check answers", () => {
    cy.request(`${API_URL}/health-check/`).its("status").should("eq", 200)
  })

  it("WFS GetCapabilities answers", () => {
    cy.request(`${API_URL}/wfs/?SERVICE=WFS&REQUEST=GetCapabilities`).then((response) => {
      expect(response.status).to.eq(200)
      expect(response.body).to.contain("WFS_Capabilities")
    })
  })
})

describe("Map layers", () => {
  RASTER_LAYERS.forEach((layer) => {
    it(`loads ${layer.key} tiles`, () => {
      cy.intercept("GET", "**/api/tiles/heat/**").as("tiles")
      cy.visit(`/${layer.key}/${MAP_POSITION}`)
      cy.getBySel("map-component").should("exist")
      cy.get("@consoleInfo").should("have.been.calledWithMatch", /cypress: map data .* loaded/)
      cy.wait("@tiles").its("response.statusCode").should("be.oneOf", [200, 204])
      cy.getBySel("raster-legend").should("exist")
    })
  })
})

describe("Pages", () => {
  it("legal mentions render", () => {
    cy.visit("/mentions-legales")
    cy.get(".legal-title").should("contain", "Informations légales")
  })
})
