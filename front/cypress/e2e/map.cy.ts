/// <reference types="cypress" />
import { DataType, DataTypeToLabel, MapStyle } from "../../src/utils/enum"
import { GEOCODER_API_URL } from "../../src/utils/geocoder"
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const MOBILE_VIEWPORT = { width: 375, height: 667 }
const DESKTOP_VIEWPORT = { width: 1440, height: 900 }

describe("Map - Desktop", () => {
  beforeEach(() => {
    cy.viewport(DESKTOP_VIEWPORT.width, DESKTOP_VIEWPORT.height)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.intercept("GET", "**/api/qpv/", { fixture: "qpv.json" }).as("qpvData")
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data Plan loaded")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("loads with plantability layer", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
  })

  it("changes map style via background selector", () => {
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.get("@consoleInfo").should("not.have.been.calledWith", "cypress: QPV data loaded") // #344

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("changes to cadastre map style", () => {
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.CADASTRE}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("switches data layer via sidebar", () => {
    // Desktop uses sidebar layer switcher (filter visible to exclude mobile hidden elements)
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
  })

  it("shows plantability context data", () => {
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Zommez et cliquez sur un carreau")
    cy.mapZoomTo(3)
    cy.getBySel("map-component").click("center")
  })

  it("shows vulnerability context data", () => {
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()

    cy.getBySel("map-context-data").should("contain", "Cliquez sur une zone")
  })

  it("shows climate zone context data", () => {
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.CLIMATE_ZONE]).click()
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Cliquez sur un carreau")
  })

  it("adds QPV layer when toggled", () => {
    // Desktop QPV toggle is in the sidebar
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(false)
  })

  it("maintains QPV layer when switching data layers", () => {
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.CLIMATE_ZONE]).click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
    cy.mapCheckQPVLayer(true)
  })

  it("maintains QPV layer when switching basemap styles", () => {
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.CADASTRE}"]`).should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.mapCheckQPVLayer(true)
  })

  it("adds cadastre layer when toggled", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
  })

  it("maintains cadastre layer when switching data layers", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
    cy.mapCheckCadastreLayer(true)
  })

  it("maintains cadastre layer when switching basemap styles", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.mapCheckCadastreLayer(true)
  })

  it("hides cadastre parcel info when layer is toggled off", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)
    cy.getBySel("cadastre-parcel-info").should("not.exist")

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
    cy.getBySel("cadastre-parcel-info").should("not.exist")
  })
})

describe("Map - Mobile", () => {
  beforeEach(() => {
    cy.viewport(MOBILE_VIEWPORT.width, MOBILE_VIEWPORT.height)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.intercept("GET", "**/api/qpv/", { fixture: "qpv.json" }).as("qpvData")
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data Plan loaded")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("loads map on mobile viewport", () => {
    cy.getBySel("map-component").should("exist")
  })

  it("opens mobile config drawer and switches data layer", () => {
    // Open config drawer via toggle button
    cy.getBySel("drawer-toggle").should("be.visible").click()

    // Mobile uses drawer layer switcher
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()

    cy.getBySel("drawer-close").click()
  })

  it("toggles QPV layer on mobile", () => {
    // Open config drawer
    cy.getBySel("drawer-toggle").should("be.visible").click()

    // Toggle QPV
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(false)
  })

  it("toggles cadastre layer on mobile", () => {
    cy.getBySel("drawer-toggle").should("be.visible").click()

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
  })

  it("changes map style on mobile via drawer", () => {
    // Open config drawer
    cy.getBySel("drawer-toggle").should("be.visible").click()

    // Use map switcher in drawer
    cy.getBySel("map-switcher").should("be.visible").click()
    cy.get(".select-option-label").contains("Images satellite").click()

    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })
})

describe("Geocoder", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data Plan loaded")
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("search for an address in Lyon and display results", () => {
    cy.get(".maplibregl-ctrl-geocoder--input", { timeout: 10000 }).should("be.visible").click()
    cy.get(".maplibregl-ctrl-geocoder--input").type("Métropole de Lyon")
    cy.intercept("GET", `${GEOCODER_API_URL}*`).as("geocoding")
    cy.wait("@geocoding")
    cy.get(".maplibregl-ctrl-geocoder .suggestions").should("be.visible")
    cy.get(".maplibregl-ctrl-geocoder .suggestions li").should("have.length.at.least", 5)
  })
})

describe("Welcome message", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.55430")
  })

  it("Close when clicked and don't show up again", () => {
    cy.getBySel("welcome-dialog").should("be.visible")
    cy.getBySel("welcome-click").should("be.visible").click()
    cy.getBySel("welcome-dialog").should("not.exist")
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.getBySel("welcome-dialog").should("not.exist")
  })
})
