// https://on.cypress.io/api

import { DataType, DataTypeToLabel } from "../../src/utils/enum"
import { GEOCODER_API_URL } from "../../src/utils/geocoder"

/*describe("Map interactions", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
  })

  it("Map loading seems to be okay", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })

  it("Verifies map layer switching and popup behavior", () => {
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.PLANTABILITY])
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup()
    cy.getBySel("plantability-score-label").should("exist")

    cy.mapSwitchLayer(DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES]) // cf. issue #142
    cy.url().should("include", "/lcz/")
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES])
    cy.mapHasNoPopup()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup()
    cy.getBySel("lcz-score-popup-title").should("exist")
    cy.mapClosePopup()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup() // cf. issue #92

    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
    cy.url().should("include", "/vulnerability/")
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.VULNERABILITY])
    cy.mapHasNoPopup()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup()
    cy.getBySel("vulnerability-score-popup-title").should("exist")

    cy.visit("/lcz/13/45.07126/5.5543")
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES])
  })
})*/

describe("Geocoder functionality", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(500)
  })

  it("search for an address in Lyon and display results", () => {
    cy.get(".maplibregl-ctrl-geocoder--input").click()
    cy.get(".maplibregl-ctrl-geocoder--input").type("Métropole de Lyon")

    cy.intercept("GET", `${GEOCODER_API_URL}*`).as("geocoding")
    cy.wait("@geocoding")
    cy.get(".maplibregl-ctrl-geocoder .suggestions").should("be.visible")
    cy.get(".maplibregl-ctrl-geocoder .suggestions li").should("have.length.at.least", 5)
  })
})
