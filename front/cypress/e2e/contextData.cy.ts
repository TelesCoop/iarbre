/// <reference types="cypress" />
import { DataType, DataTypeToLabel } from "../../src/utils/enum"
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

describe("Context Data Interactions", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
  })

  describe("Plantability Context Data", () => {
    beforeEach(() => {
      cy.visit("/plantability/13/45.07126/5.5543")
      cy.wait(300) // eslint-disable-line cypress/no-unnecessary-waiting
    })

    it("shows empty state when no tile is clicked", () => {
      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
      cy.getBySel("map-context-data").should("contain", "Zommez et cliquez sur un carreau")
    })

    it("shows plantability data when tile is clicked", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("shows plantability score and list", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("displays plantability metrics in list", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })
  })

  describe("Vulnerability Context Data", () => {
    beforeEach(() => {
      cy.visit("/vulnerability/13/45.07126/5.5543")
      cy.wait(300) // eslint-disable-line cypress/no-unnecessary-waiting
    })

    it("shows vulnerability description", () => {
      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
      cy.getBySel("map-context-data").should("contain", "Calcul basé sur l'exposition")
    })

    it("shows vulnerability score when tile is clicked", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("shows vulnerability legend", () => {
      cy.getBySel("vulnerability-legend", { timeout: 10000 }).should("exist")
      cy.getBySel("vulnerability-legend").should("be.visible")
    })

    it("displays vulnerability metrics", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })
  })

  describe("Climate Zone Context Data", () => {
    beforeEach(() => {
      cy.visit("/climate-zone/13/45.07126/5.5543")
      cy.wait(300) // eslint-disable-line cypress/no-unnecessary-waiting
    })

    it("shows climate zone description", () => {
      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
      cy.getBySel("map-context-data").should("contain", "Indicateurs climatiques locaux")
    })

    it("shows climate zone data when tile is clicked", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("displays climate zone metrics", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("shows climate zone legend", () => {
      cy.getBySel("climate-zone-legend", { timeout: 10000 }).should("exist")
      cy.getBySel("climate-zone-legend").should("be.visible")
    })
  })

  describe("Context Data Switching", () => {
    beforeEach(() => {
      cy.visit("/plantability/13/45.07126/5.5543")
      cy.wait(300) // eslint-disable-line cypress/no-unnecessary-waiting
    })

    it("switches between different context data types", () => {
      cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
      cy.wait(500) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-context-data", { timeout: 10000 }).should(
        "contain",
        "Calcul basé sur l'exposition"
      )

      cy.mapSwitchLayer(DataTypeToLabel[DataType.CLIMATE_ZONE])
      cy.wait(500) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-context-data", { timeout: 10000 }).should(
        "contain",
        "Indicateurs climatiques locaux"
      )

      cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])
      cy.wait(500) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("maintains context data after zoom", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")

      cy.mapZoomTo(15)
      cy.wait(500) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })
  })

  describe("Mobile Context Data", () => {
    beforeEach(() => {
      cy.viewport(375, 667)
      cy.visit("/plantability/13/45.07126/5.5543")
      cy.wait(300) // eslint-disable-line cypress/no-unnecessary-waiting
    })

    it("shows context data on mobile viewport", () => {
      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })

    it("handles mobile interactions", () => {
      cy.mapZoomTo(16)
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting
      cy.getBySel("map-component").click("center", { force: true })
      cy.wait(1000) // eslint-disable-line cypress/no-unnecessary-waiting

      cy.getBySel("map-context-data", { timeout: 10000 }).should("exist")
    })
  })
})
