/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const DESKTOP_VIEWPORT = { width: 1440, height: 900 }

describe("Dashboard - Print Mode", () => {
  beforeEach(() => {
    cy.viewport(DESKTOP_VIEWPORT.width, DESKTOP_VIEWPORT.height)
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.intercept("GET", "**/api/dashboard/", { fixture: "dashboard.json" }).as("dashboard")
    cy.visit("/dashboard?print=1")
    cy.wait("@dashboard")
  })

  it("does not render the sidebar in print mode", () => {
    cy.get("aside.sidebar").should("not.exist")
  })

  it("does not render the footer download button in print mode", () => {
    cy.contains("Télécharger").should("not.exist")
  })

  it("renders widget cards", () => {
    cy.get(".widget-card").should("have.length.greaterThan", 0)
  })

  it("renders all four narrative sections", () => {
    cy.get(".narrative-section").should("have.length", 4)
  })

  it("sets window.__DASHBOARD_READY__ after data loads and renders", () => {
    cy.window().its("__DASHBOARD_READY__").should("eq", true)
  })
})
