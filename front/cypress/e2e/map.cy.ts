import { DataType, DataTypeToLabel, MapStyle } from "../../src/utils/enum"
import { GEOCODER_API_URL } from "../../src/utils/geocoder"

describe("Map", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(150)
  })
  it("loads with plantability layer", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })
  it("changes map style", () => {
    cy.basemapSwitchLayer(MapStyle.SATELLITE)
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.basemapSwitchLayer(MapStyle.OSM)
    // check that layer is loaded
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })
  it("switches layer", () => {
    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
    cy.mapHasNoPopup()
    cy.wait(100) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup()
    cy.getBySel("vulnerability-score-popup").should("exist")
    cy.contains("Vulnérabilité moyenne à élevée").should("exist")
    cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])
    cy.mapHasNoPopup()
    cy.mapOpenPopup()
    cy.getBySel("plantability-score-popup").should("exist")
  })
  it("shows plantability context data", () => {
    cy.getBySel("map-context-data").should("not.exist")
    cy.mapOpenPopup()
    cy.getBySel("toggle-plantability-score-details").click()
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Score de plantabilité")
    cy.getBySel("close-plantability-context-data").click()
    cy.getBySel("map-context-data").should("not.exist")
  })
})

describe("Geocoder", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(200)
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
