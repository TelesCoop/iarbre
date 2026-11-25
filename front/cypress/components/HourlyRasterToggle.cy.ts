/// <reference types="cypress" />
import HourlyRasterToggle from "@/components/contextTools/HourlyRasterToggle.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("HourlyRasterToggle", () => {
  beforeEach(() => {
    cy.mount(HourlyRasterToggle)
    cy.window().then(() => {
      useMapStore().selectedDataType = DataType.PET
      useMapStore().setRasterHour(9)
    })
  })

  it("toggles between comfort and shadow and keeps the hour", () => {
    cy.get('[data-cy="hourly-raster-toggle"] [role="switch"]')
      .should("have.attr", "aria-checked", "false")
      .click()
    cy.window().should(() => {
      expect(useMapStore().selectedDataType).to.eq(DataType.SHADOW)
      expect(useMapStore().rasterHour).to.eq(9)
    })
    cy.get('[data-cy="hourly-raster-toggle"] [role="switch"]')
      .should("have.attr", "aria-checked", "true")
      .click()
    cy.window().should(() => expect(useMapStore().selectedDataType).to.eq(DataType.PET))
  })
})
