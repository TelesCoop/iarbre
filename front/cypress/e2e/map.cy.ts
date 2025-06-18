import { DataType, DataTypeToLabel, MapStyle } from "../../src/utils/enum"
import { GEOCODER_API_URL } from "../../src/utils/geocoder"

describe("Map", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data Plan loaded")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })
  it("shows vulnerability context data", () => {
    // will be restored in a later PR
    cy.getBySel("map-context-data").should("not.exist")
    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
    cy.getBySel("map-context-data").should("not.exist")
    cy.mapOpenPopup()
    // Check if the popup actually contains vulnerability data before trying to open details
    cy.getBySel("vulnerability-score-popup").should("exist")
    // Check if the details button exists and is clickable
    cy.getBySel("toggle-vulnerability-score-details").should("be.visible")
    cy.getBySel("toggle-vulnerability-score-details").click()

    // The context data should appear (or show an empty message if no data)
    cy.getBySel("map-context-data").should("exist")

    cy.getBySel("map-context-data").should("satisfy", ($el) => {
      const text = $el.text()
      return text.includes("Vulnérabilité à la chaleur") || text.includes("Aucune donnée")
    })

    //cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])
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
  it("changes to cadastre map style", () => {
    cy.basemapSwitchLayer(MapStyle.CADASTRE)
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.basemapSwitchLayer(MapStyle.OSM)
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })
  it("switches layer", () => {
    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
    cy.mapHasNoPopup()
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
    cy.getBySel("toggle-plantability-score-details").should("not.exist")
    cy.mapZoomTo(4)
    cy.getBySel("toggle-plantability-score-details").should("be.visible").click()
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Score de plantabilité")
    cy.getBySel("close-context-data").click()
    cy.getBySel("map-context-data").should("not.exist")
  })

  it("shows climate zone context data", () => {
    cy.mapSwitchLayer(DataTypeToLabel[DataType.CLIMATE_ZONE])
    cy.getBySel("map-context-data").should("not.exist")
    cy.mapOpenPopup()
    cy.getBySel("toggle-climate-zone-details").should("be.visible").click()
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Zones climatiques locales")
    cy.getBySel("close-context-data").click()
    cy.getBySel("map-context-data").should("not.exist")
  })
})

describe("Geocoder", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
  })

  it("search for an address in Lyon and display results", () => {
    cy.get(".maplibregl-ctrl-geocoder--input").should("be.visible").click()
    cy.get(".maplibregl-ctrl-geocoder--input").type("Métropole de Lyon")
    cy.intercept("GET", `${GEOCODER_API_URL}*`).as("geocoding")
    cy.wait("@geocoding")
    cy.get(".maplibregl-ctrl-geocoder .suggestions").should("be.visible")
    cy.get(".maplibregl-ctrl-geocoder .suggestions li").should("have.length.at.least", 5)
  })
})
