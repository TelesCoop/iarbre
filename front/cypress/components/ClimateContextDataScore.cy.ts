import ClimateContextDataScore from "@/components/contextData/climate/ClimateContextDataScore.vue"
import type { ClimateData } from "@/types/climate"
import { DataType, GeoLevel } from "@/utils/enum"

describe("ClimateContextDataScore.vue", () => {
  const mockClimateData: ClimateData = {
    lczIndex: "1",
    lczDescription: "Compact highrise",
    datatype: DataType.CLIMATE_ZONE,
    geolevel: GeoLevel.IRIS,
    id: 1,
    geometry: "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    mapGeometry: "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    details: {
      hre: 25,
      are: 200,
      bur: 50,
      ror: 40,
      bsr: 5,
      war: 0,
      ver: 5,
      vhr: 10
    }
  }

  it("renders with climate data", () => {
    cy.mount(ClimateContextDataScore, {
      props: {
        data: mockClimateData
      }
    })

    cy.contains("Zone climatique locale").should("be.visible")
    cy.contains("Compact highrise").should("be.visible")
  })

  it("displays correct zone description", () => {
    const customData = {
      ...mockClimateData,
      lczDescription: "Open lowrise"
    }

    cy.mount(ClimateContextDataScore, {
      props: {
        data: customData
      }
    })

    cy.contains("Open lowrise").should("be.visible")
  })

  it("applies background color based on zone", () => {
    cy.mount(ClimateContextDataScore, {
      props: {
        data: mockClimateData
      }
    })

    cy.get(".map-context-card").should("have.attr", "style").and("include", "background-color")
  })

  it("handles missing lczIndex gracefully", () => {
    const dataWithoutIndex = {
      ...mockClimateData,
      lczIndex: ""
    }

    cy.mount(ClimateContextDataScore, {
      props: {
        data: dataWithoutIndex
      }
    })

    cy.get(".map-context-card").should("exist")
  })

  it("has correct text styling classes", () => {
    cy.mount(ClimateContextDataScore, {
      props: {
        data: mockClimateData
      }
    })

    cy.get(".map-context-card").should("have.class", "text-lg")
    cy.get("span").should("have.class", "text-center")
  })

  it("displays full label text", () => {
    cy.mount(ClimateContextDataScore, {
      props: {
        data: mockClimateData
      }
    })

    cy.get(".map-context-card").should("contain", "Zone climatique locale :")
    cy.get(".map-context-card").should("contain", mockClimateData.lczDescription)
  })
})
