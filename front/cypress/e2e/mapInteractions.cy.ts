// https://on.cypress.io/api

import { DataType, DataTypeToLabel } from "../../src/utils/enum"
import { GEOCODER_SELECTORS, GEOCODER_STYLE } from "../../src/utils/geocoder"

describe("Map interactions", () => {
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
})

describe("Geocoder functionality", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(500)
  })

  it("expand search bar on click", () => {
    cy.get(GEOCODER_SELECTORS.CONTAINER).should(
      "have.css",
      "width",
      GEOCODER_STYLE.COLLAPSED.CONTAINER_WIDTH
    )

    cy.get(GEOCODER_SELECTORS.CONTAINER).click()
    cy.get(GEOCODER_SELECTORS.CONTAINER).should(
      "have.css",
      "width",
      GEOCODER_STYLE.EXPANDED.CONTAINER_WIDTH
    )
    cy.get(GEOCODER_SELECTORS.INPUT).should("be.focused")
  })

  it("collapse search bar when clicking outside", () => {
    cy.get(GEOCODER_SELECTORS.CONTAINER).click()
    cy.get(GEOCODER_SELECTORS.CONTAINER).should(
      "have.css",
      "width",
      GEOCODER_STYLE.EXPANDED.CONTAINER_WIDTH
    )
    cy.getBySel("map-component").click("center")
    cy.get(GEOCODER_SELECTORS.CONTAINER).should(
      "have.css",
      "width",
      GEOCODER_STYLE.COLLAPSED.CONTAINER_WIDTH
    )
  })

  it("search for an address in Villars and display results", () => {
    cy.get(GEOCODER_SELECTORS.CONTAINER).click()
    cy.get(GEOCODER_SELECTORS.INPUT).type("Rue du Vercors")
    cy.get(GEOCODER_SELECTORS.INPUT).type("{enter}")

    cy.intercept("GET", "https://api-adresse.data.gouv.fr/search/*").as("geocoding")
    cy.wait("@geocoding")

    cy.get(".suggestions").should("be.visible")
    cy.get(".suggestions li").should("have.length.at.least", 2)
  })
})
