import MapPlantabilityLegend from "../../src/components/map/legend/PlantabilityLegend.vue"

describe("Component:MapPlantabilityLegend", () => {
  it("renders correctly", () => {
    cy.mount(MapPlantabilityLegend)

    cy.contains(0)
    cy.contains(2)
    cy.contains(4)
    cy.contains(6)
    cy.contains(8)
    cy.contains(10)
    cy.contains("Plantable")
    cy.contains("Non plantable")
  })
})
