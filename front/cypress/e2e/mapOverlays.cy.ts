/// <reference types="cypress" />
import { DESKTOP_VIEWPORT, MOBILE_VIEWPORT } from "../support/viewports"

const expectBackgroundSelectorExpanded = (isExpanded: boolean) =>
  cy.getBySel("bg-selector-toggle").should("have.attr", "aria-expanded", String(isExpanded))

/** A spot of the mobile map that no overlay covers: right column, below the search bar. */
const tapMap = () => cy.getBySel("map-component").click(270, 200)

describe("Map overlays - Mobile", () => {
  beforeEach(() => cy.visitMap(MOBILE_VIEWPORT))

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

  it("closes the shape panel with Escape from the toolbar only", () => {
    cy.getBySel("shape-toolbar-toggle").click()

    cy.get("[data-cy='map-geocoder'] input").trigger("keydown", { key: "Escape" })
    cy.getBySel("shape-toolbar").should("be.visible")

    cy.getBySel("shape-toolbar-toggle").trigger("keydown", { key: "Escape" })
    cy.getBySel("shape-toolbar").should("not.exist")
  })
})

describe("Map overlays - Desktop", () => {
  beforeEach(() => cy.visitMap(DESKTOP_VIEWPORT))

  it("keeps the background selector open while the map is dragged", () => {
    cy.getBySel("bg-selector-toggle").click()

    cy.getBySel("map-component").trigger("pointerdown", 700, 300)
    cy.getBySel("map-component").trigger("click", 800, 400)

    expectBackgroundSelectorExpanded(true)
  })
})
