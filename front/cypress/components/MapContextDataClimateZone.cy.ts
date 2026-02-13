/// <reference types="cypress" />
import MapContextDataClimateZone from "@/components/contextData/MapContextDataClimateZone.vue"
import { DataType, GeoLevel } from "@/utils/enum"
import type { ClimateData } from "@/types/climate"
import { ClimateDataDetailsKey } from "@/types/climate"
import { ClimateCategory } from "@/types/climate"
import { useClimateZone } from "@/composables/useClimateZone"

describe("MapContextDataClimateZone", () => {
  const mockClimateData: ClimateData = {
    datatype: DataType.CLIMATE,
    geolevel: GeoLevel.LCZ,
    lczDescription: "Ensemble dense de batîments hauts",
    id: 123,
    details: {
      [ClimateDataDetailsKey.HRE]: 15.5,
      [ClimateDataDetailsKey.ARE]: 250.0
    }
  }

  it("display climate zone data correctly", () => {
    cy.mount(MapContextDataClimateZone, {
      props: {
        data: mockClimateData
      }
    })

    cy.contains("Ensemble dense de batîments hauts").should("be.visible")
  })

  it("display climate metrics with categories", () => {
    cy.mount(MapContextDataClimateZone, {
      props: {
        data: mockClimateData
      }
    })

    const { climateCategoryKey } = useClimateZone()
    cy.contains(ClimateCategory.BUILDING).should("be.visible")
    cy.getBySel(`category-${climateCategoryKey[ClimateCategory.BUILDING]}`).click()
    cy.contains("Hauteur moyenne du bâti").should("be.visible")
    cy.contains("15.5").should("be.visible")
    cy.contains("Superficie moyenne du bâti").should("be.visible")
    cy.contains("250").should("be.visible")
  })

  it("display empty message when climate data is null", () => {
    cy.mount(MapContextDataClimateZone, {
      props: {
        data: null
      }
    })

    cy.get('[data-cy="empty-message"]').should("exist")
  })
})
