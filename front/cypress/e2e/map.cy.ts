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
  it.skip("shows vulnerability context data", () => {
    cy.getBySel("map-context-data").should("not.exist")
    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])

    cy.getBySel("map-context-data").should("satisfy", ($el) => {
      const text = $el.text()
      return text.includes("Vulnérabilité chaleur") || text.includes("Cliquez sur une zone")
    })
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
    cy.get("@consoleInfo").should("not.have.been.calledWith", "cypress: QPV data loaded") // #344
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

    cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])
  })
  it("shows plantability context data", () => {
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Zommez et cliquez sur un carreau")
    cy.mapZoomTo(4)
    cy.getBySel("map-component").click("center")
    cy.wait(500) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.getBySel("map-context-data").should("contain", "Paramètres principaux")
  })

  it.skip("shows climate zone context data", () => {
    cy.mapSwitchLayer(DataTypeToLabel[DataType.CLIMATE_ZONE])
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Zones climatiques locales")
  })

  it("adds QPV layer when toggled", () => {
    cy.getBySel("qpv-toggle").should("be.visible").click()

    cy.mapCheckQPVLayer(true)

    cy.getBySel("qpv-toggle").should("be.visible").click()

    cy.mapCheckQPVLayer(false)
  })

  it("maintains QPV layer when switching data layers", () => {
    cy.getBySel("qpv-toggle").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
    cy.mapCheckQPVLayer(true)

    cy.mapSwitchLayer(DataTypeToLabel[DataType.CLIMATE_ZONE])
    cy.mapCheckQPVLayer(true)

    cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])
    cy.mapCheckQPVLayer(true)
  })

  it("maintains QPV layer when switching basemap styles", () => {
    cy.getBySel("qpv-toggle").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.basemapSwitchLayer(MapStyle.SATELLITE)
    cy.mapCheckQPVLayer(true)

    cy.basemapSwitchLayer(MapStyle.CADASTRE)
    cy.mapCheckQPVLayer(true)

    cy.basemapSwitchLayer(MapStyle.OSM)
    cy.mapCheckQPVLayer(true)
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
