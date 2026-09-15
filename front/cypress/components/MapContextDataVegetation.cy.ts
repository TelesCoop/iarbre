/// <reference types="cypress" />
import MapContextDataVegetation from "@/components/contextData/MapContextDataVegetation.vue"
import { useMapStore } from "@/stores/map"
import { DataType, GeoLevel } from "@/utils/enum"
import type { VegetationData } from "@/types/vegetation"

const mockVegetationData: VegetationData = {
  id: "1",
  indice: "arborescent",
  surface: 25,
  geolevel: GeoLevel.TILE,
  datatype: DataType.VEGESTRATE
}

describe("MapContextDataVegetation - height mode", () => {
  beforeEach(() => {
    cy.mount(MapContextDataVegetation)
    cy.window().then(() => {
      const store = useMapStore()
      store.showVegestrateHeight = true
      store.vegetationHeightAtPoint = undefined
    })
  })

  it("shows the gauge when height mode is active", () => {
    cy.get(".height-gauge-container").should("exist")
  })

  it("empty message says to click a pixel", () => {
    cy.contains("Cliquez sur un pixel.").should("be.visible")
  })

  it("shows height value in the gauge after a click", () => {
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = 15
    })
    cy.contains("15").should("be.visible")
    cy.contains("m").should("be.visible")
  })

  it("shows 'Hors zone' when height is null", () => {
    cy.window().then(() => {
      useMapStore().vegetationHeightAtPoint = null
    })
    cy.contains("Hors zone").should("be.visible")
  })
})

describe("MapContextDataVegetation - tile mode", () => {
  it("shows the tile data when height mode is off and data is provided", () => {
    cy.mount(MapContextDataVegetation, { props: { data: mockVegetationData } })
    cy.window().then(() => {
      useMapStore().showVegestrateHeight = false
    })
    cy.get(".height-gauge-container").should("not.exist")
  })

  it("empty message says to click a tile when height mode is off", () => {
    cy.mount(MapContextDataVegetation)
    cy.window().then(() => {
      useMapStore().showVegestrateHeight = false
    })
    cy.contains("Cliquez sur un carreau.").should("be.visible")
  })
})
