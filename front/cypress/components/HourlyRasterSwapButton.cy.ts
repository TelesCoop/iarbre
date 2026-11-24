/// <reference types="cypress" />
import HourlyRasterSwapButton from "@/components/layerSwitcher/HourlyRasterSwapButton.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("HourlyRasterSwapButton", () => {
  beforeEach(() => {
    cy.mount(HourlyRasterSwapButton)
    cy.window().then(() => {
      useMapStore().selectedDataType = DataType.PET
      useMapStore().setRasterHour(9)
    })
  })

  it("swaps between comfort and shadow and keeps the hour", () => {
    cy.get('[data-cy="hourly-raster-swap"]').should("contain.text", "Voir l'ombre à 9h").click()
    cy.window().should(() => {
      expect(useMapStore().selectedDataType).to.eq(DataType.SHADOW)
      expect(useMapStore().rasterHour).to.eq(9)
    })
    cy.get('[data-cy="hourly-raster-swap"]').should("contain.text", "Voir le confort à 9h").click()
    cy.window().should(() => expect(useMapStore().selectedDataType).to.eq(DataType.PET))
  })
})
