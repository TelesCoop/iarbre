// https://on.cypress.io/api

import { DataType, DataTypeToLabel } from "../../src/utils/enum"

describe("Map interactions", () => {
  beforeEach(() => {
    cy.visit("/13/45.07126/5.5543")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data loaded")
  })

  it("Map loading seems to be okay", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
    cy.contains("OpenStreetMap Contributors").should("exist")
  })

  it.skip("Verifies map layer switching and popup behavior", () => {
    // eslint-disable-line cypress/no-unnecessary-waiting
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.PLANTABILITY])
    cy.mapOpenPopup()
    cy.getBySel("plantability-score-label").should("exist")

    cy.mapSwitchLayer(DataType.LOCAL_CLIMATE_ZONES) // cf. issue #142
    cy.getBySel("map-legend-title").should("contain", DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES])
    cy.mapHasNoPopup()
    cy.wait(2000) // eslint-disable-line cypress/no-unnecessary-waiting
    cy.mapOpenPopup()
    cy.getBySel("lcz-score-popup-title").should("exist")
    cy.mapClosePopup()
    cy.mapOpenPopup() // cf. issue #92
  })
})
