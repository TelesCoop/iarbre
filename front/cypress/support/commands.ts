/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const DEFAULT_MAP_PATH = "/plantability/13/45.07126/5.55430"

const getMapStore = (win: Window) =>
  (win.document.querySelector("#app") as any).__vue_app__.config.globalProperties.$pinia._s.get(
    "map"
  )

/**
 * Custom command to get element by data-cy attribute
 */
Cypress.Commands.add("getBySel", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

/**
 * Custom command to switch data layer on desktop (via sidebar)
 * @deprecated Use direct selectors in tests for better clarity
 */
Cypress.Commands.add("mapSwitchLayer", (datatype: string) => {
  cy.getBySel("layer-switcher").filter(":visible").first().should("be.visible").click()
  cy.get(".p-select-option-label").contains(datatype).click()
})

/**
 * Custom command to switch basemap style on desktop (via background selector)
 * @deprecated Use direct selectors in tests for better clarity
 */
Cypress.Commands.add("basemapSwitchLayer", (maptype: string) => {
  cy.getBySel("bg-selector-toggle").filter(":visible").first().should("be.visible").click()
  cy.get(`[data-cy="bg-option-${maptype}"]`).should("be.visible").click()
})

/**
 * Custom command to zoom in on map
 */
Cypress.Commands.add("mapZoomTo", (zoom: number) => {
  for (let i = 1; i < zoom + 1; i++) {
    cy.get(".maplibregl-ctrl-zoom-in").should("be.visible").click()
    cy.wait(200) // eslint-disable-line cypress/no-unnecessary-waiting
  }
})

/**
 * Opens the map past the welcome message, once its plantability layer is loaded
 */
Cypress.Commands.add(
  "visitMap",
  (viewport: { width: number; height: number }, path: string = DEFAULT_MAP_PATH) => {
    cy.viewport(viewport.width, viewport.height)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.intercept("GET", "**/api/qpv/", { fixture: "qpv.json" }).as("qpvData")
    cy.visit(path)
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  }
)

/**
 * Yields the map Pinia store of the running app, the single place tests reach into app internals
 */
Cypress.Commands.add("mapStore", () => cy.window().then(getMapStore))

/**
 * Custom command to check QPV layer status via console logs
 */
Cypress.Commands.add("mapCheckQPVLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist ? "cypress: QPV data loaded" : "cypress: QPV data removed"
  cy.get("@consoleInfo").should("have.been.calledWith", expectedMessage)
})

Cypress.Commands.add("mapCheckCadastreLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist
    ? "cypress: cadastre data loaded"
    : "cypress: cadastre data removed"
  cy.get("@consoleInfo").should("have.been.calledWith", expectedMessage)
})

Cypress.Commands.add("mapCheckPanoramaxLayer", (shouldExist: boolean) => {
  const expectedMessage = shouldExist
    ? "cypress: panoramax data loaded"
    : "cypress: panoramax data removed"
  cy.get("@consoleInfo").should((spy: any) => {
    const messages: string[] = spy.args
      .map((args: unknown[]) => args[0])
      .filter((message: unknown): message is string =>
        typeof message === "string" ? message.startsWith("cypress: panoramax data") : false
      )
    expect(messages[messages.length - 1]).to.equal(expectedMessage)
  })
})
