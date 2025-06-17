import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapContextDataClimateZone from "@/components/contextData/MapContextDataClimateZone.vue"
import { DataType, GeoLevel } from "@/utils/enum"
import type { ClimateData } from "@/types/climate"
import { ClimateDataDetailsKey } from "@/types/climate"

describe("MapContextDataClimateZone", () => {
  const mockClimateData: ClimateData = {
    datatype: DataType.CLIMATE,
    geolevel: GeoLevel.LCZ,
    id: 123,
    details: {
      [ClimateDataDetailsKey.HRE]: 15.5,
      [ClimateDataDetailsKey.ARE]: 250.0
    }
  }

  it("display climate zone data correctly", () => {
    const pinia = createPinia()

    mount(MapContextDataClimateZone, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockClimateData
      }
    })

    cy.contains("Zones climatiques locales").should("be.visible")
    cy.contains("Indicateurs climatiques locaux pour une zone sélectionnée").should("be.visible")
  })

  it("display close button and emit close event", () => {
    const pinia = createPinia()

    mount(MapContextDataClimateZone, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockClimateData
      }
    })

    cy.get('[data-cy="close-context-data"]').should("be.visible")
    cy.get('[data-cy="close-context-data"]').click()
  })

  it("display climate metrics with categories", () => {
    const pinia = createPinia()

    mount(MapContextDataClimateZone, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockClimateData
      }
    })

    cy.contains("Caractéristiques du bâti").should("be.visible")

    cy.contains("Hauteur moyenne du bâti").should("be.visible")
    cy.contains("15.5").should("be.visible")
    cy.contains("Superficie moyenne du bâti").should("be.visible")
    cy.contains("250").should("be.visible")
  })
})
