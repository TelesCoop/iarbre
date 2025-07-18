/// <reference types="cypress" />
import MapscorePopup from "@/components/map/popup/MapScorePopup.vue"
import { createPinia, setActivePinia } from "pinia"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { PlantabilityScore } from "@/types/plantability"
import { getVulnerabilityScoreLabel, VulnerabilityType } from "@/utils/vulnerability"

describe("MapScorePopup", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it(`renders correctly when the selected map data type is ${DataType.PLANTABILITY}`, () => {
    const mapStore = useMapStore()
    mapStore.selectedDataType = DataType.PLANTABILITY
    mapStore.popupData = {
      id: "e",
      score: "8",
      lat: 45.76,
      lng: 4.85
    }

    cy.mount(MapscorePopup)
    cy.contains("8/10")
    cy.contains("45.76")
    cy.contains("4.85")
    cy.contains(PlantabilityScore.FAVORED)
  })

  it(`renders correctly when the selected map data type is ${DataType.CLIMATE_ZONE}`, () => {
    const mapStore = useMapStore()
    mapStore.selectedDataType = DataType.CLIMATE_ZONE
    mapStore.popupData = {
      id: "E",
      score: "E",
      lat: 12.34,
      lng: 56.78
    }

    cy.mount(MapscorePopup)
    cy.contains("LCZ")
    cy.contains("Sol imperméable naturel ou artificiel")
    cy.contains("12.34000° N, 56.78000° E")
  })
  it(`renders correctly when the selected map data type is ${DataType.VULNERABILITY}`, () => {
    const mapStore = useMapStore()
    mapStore.selectedDataType = DataType.VULNERABILITY
    mapStore.popupData = {
      id: "E",
      lat: 12.34,
      lng: 56.78,
      properties: {
        indice_day: 8,
        indice_night: 10,
        expo_index_day: 1,
        expo_index_night: 2,
        capaf_index_day: 3,
        capaf_index_night: 4,
        sensibilty_index_day: 5,
        sensibilty_index_night: 6
      }
    }
    cy.mount(MapscorePopup)
    cy.contains("en journée")
    cy.contains(getVulnerabilityScoreLabel[VulnerabilityType.EXPOSITION])
    cy.contains(getVulnerabilityScoreLabel[VulnerabilityType.DIFFICULTY_TO_FACE])
    cy.contains(getVulnerabilityScoreLabel[VulnerabilityType.SENSIBILITY])

    // Should display the vulnerability scores correctly
    cy.contains(1) // expo_index_day
    cy.contains(3) // capaf_index_day
    cy.contains(5) // sensibilty_index_day

    cy.contains("12.34000° N, 56.78000° E")
  })
})
