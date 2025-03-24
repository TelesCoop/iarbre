/// <reference types="cypress" />
import { mount } from "cypress/vue"
import MapscorePopup from "@/components/map/popup/MapScorePopup.vue"
import { createPinia, setActivePinia } from "pinia"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("MapscorePopup Component", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("MapPopUp when selectedDataType is PLANTABILITY", () => {
    const mapStore = useMapStore()
    mapStore.selectedDataType = DataType.PLANTABILITY

    mount(MapscorePopup, {
      props: {
        index: "0.81",
        lat: 45.76,
        lng: 4.85
      }
    })
    cy.contains("8/10")
    cy.contains("45.76")
    cy.contains("4.85")
    cy.contains("Plantabilité élevée")
  })

  it("MapPopUp when selectedDataType is LOCAL_CLIMATE_ZONES", () => {
    const mapStore = useMapStore()
    mapStore.selectedDataType = DataType.LOCAL_CLIMATE_ZONES

    mount(MapscorePopup, {
      props: {
        index: "E",
        lat: 12.34,
        lng: 56.78
      }
    })
    cy.contains("LCZ")
    cy.contains("Sol imperméable naturel ou artificiel")
  })
})
