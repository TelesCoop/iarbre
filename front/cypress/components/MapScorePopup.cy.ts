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
  it("renders correctly", () => {
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
