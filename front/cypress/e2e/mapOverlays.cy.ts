/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const MOBILE_VIEWPORT = { width: 375, height: 667 }

const expectBackgroundSelectorExpanded = (isExpanded: boolean) =>
  cy.getBySel("bg-selector-toggle").should("have.attr", "aria-expanded", String(isExpanded))

/** A spot of the mobile map that no overlay covers: right column, below the search bar. */
const tapMap = () => cy.getBySel("map-component").click(270, 200)

describe("Map overlays - Mobile", () => {
  beforeEach(() => {
    cy.viewport(MOBILE_VIEWPORT.width, MOBILE_VIEWPORT.height)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("folds the background selector when the map is tapped", () => {
    cy.getBySel("bg-selector-toggle").click()
    expectBackgroundSelectorExpanded(true)

    tapMap()

    expectBackgroundSelectorExpanded(false)
  })

  it("folds the background selector when the shape tool is opened", () => {
    cy.getBySel("bg-selector-toggle").click()

    cy.getBySel("shape-toolbar-toggle").click()

    expectBackgroundSelectorExpanded(false)
    cy.getBySel("shape-toolbar").should("be.visible")
  })

  it("folds the shape panel when the map is tapped", () => {
    cy.getBySel("shape-toolbar-toggle").click()

    tapMap()

    cy.getBySel("shape-toolbar").should("not.exist")
  })

  it("keeps the shape panel open while a shape is drawn on the map", () => {
    cy.getBySel("shape-toolbar-toggle").click()
    cy.getBySel("shape-mode-polygon").click()

    tapMap()

    cy.getBySel("shape-toolbar").should("be.visible")
  })

  it("folds the shape panel when the background selector is opened, even while drawing", () => {
    cy.getBySel("shape-toolbar-toggle").click()
    cy.getBySel("shape-mode-polygon").click()

    cy.getBySel("bg-selector-toggle").click()

    cy.getBySel("shape-toolbar").should("not.exist")
    expectBackgroundSelectorExpanded(true)
  })
})
