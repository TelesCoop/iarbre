/// <reference types="cypress" />
import HourlyRasterContextTool from "@/components/contextTools/HourlyRasterContextTool.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("HourlyRasterContextTool", () => {
  beforeEach(() => {
    cy.mount(HourlyRasterContextTool)
    cy.window().then(() => {
      useMapStore().selectedDataType = DataType.PET
    })
  })

  it("switches the scenario year", () => {
    cy.get('[data-cy="raster-year-2020"]').click()
    cy.get('[data-cy="raster-year-2020"]').should("have.attr", "aria-checked", "true")
    cy.window().then(() => expect(useMapStore().rasterYear).to.eq(2020))
  })

  it("changes the hour from the slider", () => {
    cy.get('[data-cy="raster-hour-slider"]').invoke("val", 9).trigger("input")
    cy.contains("9h")
    cy.window().should(() => expect(useMapStore().rasterHour).to.eq(9))
  })

  it("keeps the hour and hides the years when switching to shadow", () => {
    cy.get('[data-cy="raster-hour-slider"]').invoke("val", 9).trigger("input")
    cy.window().should(() => expect(useMapStore().rasterHour).to.eq(9))
    cy.window().then(() => {
      useMapStore().selectedDataType = DataType.SHADOW
    })
    cy.get('[data-cy="raster-year-2020"]').should("not.exist")
    cy.get('[data-cy="raster-hour-slider"]').should("have.value", "9")
    cy.contains("9h")
  })
})
