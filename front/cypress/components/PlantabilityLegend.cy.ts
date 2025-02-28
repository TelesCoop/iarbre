import PlantabilityLegend from "@/components/map/PlantabilityLegend.vue"

describe("Component:PlantabilityLegend", () => {
  it("renders correctly", () => {
    cy.mount(PlantabilityLegend)
    cy.contains("Non plantable")
    cy.contains("Plantable")
  })
})
