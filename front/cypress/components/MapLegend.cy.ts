import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import VulnerabilityLegend from "@/components/map/legend/VulnerabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/legend/ClimateZonesLegend.vue"

describe("Map legends", () => {
  it("renders correctly plantability legend", () => {
    cy.mount(PlantabilityLegend, {})
    cy.contains(0)
    cy.contains(2)
    cy.contains(4)
    cy.contains(6)
    cy.contains(8)
    cy.contains(10)
    cy.contains("Plantable")
    cy.contains("Non plantable")
  })
  it("renders correctly vulnerability legend", () => {
    cy.mount(VulnerabilityLegend)
  })
  it("renders correctly lcz legend", () => {
    cy.mount(ClimateZonesLegend)
  })
})
