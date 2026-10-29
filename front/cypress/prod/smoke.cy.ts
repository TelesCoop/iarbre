/// <reference types="cypress" />
import { DataType } from "../../src/utils/enum"

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
  const dataTypes = [
    DataType.PLANTABILITY,
    DataType.VULNERABILITY,
    DataType.CLIMATE_ZONE,
    DataType.VEGESTRATE,
    DataType.PLANTABILITY_VULNERABILITY,
    DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY
  ]

  dataTypes.forEach((dataType) => {
    it(`loads ${dataType} tiles`, () => {
      cy.intercept("GET", "**/api/tiles/**/*.mvt").as("tiles")
      cy.visit(`/${dataType}/${MAP_POSITION}`)
      cy.getBySel("map-component").should("exist")
      cy.get("@consoleInfo").should("have.been.calledWithMatch", /cypress: map data .* loaded/)
      cy.wait("@tiles").its("response.statusCode").should("be.oneOf", [200, 204])
      cy.getBySel("map-context-data").should("exist")
    })
  })
})

describe("Pages", () => {
  it("dashboard renders with live data", () => {
    cy.intercept("GET", "**/api/dashboard/").as("dashboard")
    cy.visit("/dashboard")
    cy.wait("@dashboard").its("response.statusCode").should("eq", 200)
    cy.get(".widget-card").should("have.length.greaterThan", 0)
  })

  it("legal mentions render", () => {
    cy.visit("/mentions-legales")
    cy.get(".legal-title").should("contain", "Informations légales")
  })
})
