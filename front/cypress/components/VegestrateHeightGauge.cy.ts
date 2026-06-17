/// <reference types="cypress" />
import VegestrateHeightGauge from "@/components/contextData/vegestrate/VegestrateHeightGauge.vue"
import { useMapStore } from "@/stores/map"

describe("VegestrateHeightGauge", () => {
  it("shows 'Cliquez sur un pixel.' when no height is set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = undefined
    })
    cy.contains("Cliquez sur un pixel.").should("be.visible")
  })

  it("shows 'Hors zone' when height is null (outside raster)", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = null
    })
    cy.contains("Hors zone").should("be.visible")
  })

  it("shows the height value and unit when set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = 12
    })
    cy.contains("12").should("be.visible")
    cy.contains("m").should("be.visible")
    cy.contains("Hors zone").should("not.exist")
  })

  it("renders the gauge bar with a gradient", () => {
    cy.mount(VegestrateHeightGauge)
    cy.get(".gauge-bar").should("have.attr", "style").and("include", "linear-gradient")
  })

  it("gauge bar is dimmed when no height is set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = undefined
    })
    cy.get(".gauge-bar").should("have.class", "gauge-bar--idle")
  })

  it("gauge bar is not dimmed when height is set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = 8
    })
    cy.get(".gauge-bar").should("not.have.class", "gauge-bar--idle")
  })

  it("shows a marker when height is set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = 20
    })
    cy.get(".gauge-marker").should("exist")
  })

  it("hides the marker when no height is set", () => {
    cy.mount(VegestrateHeightGauge)
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = undefined
    })
    cy.get(".gauge-marker").should("not.exist")
  })

  it("renders tick labels", () => {
    cy.mount(VegestrateHeightGauge)
    cy.contains("0m").should("exist")
    cy.contains("40m").should("exist")
  })
})
