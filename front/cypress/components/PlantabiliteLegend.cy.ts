import PlantabiliteLegend from "@/components/map/PlantabiliteLegend.vue"

describe("Component:PlantabiliteLegend", () => {
  it("renders correctly", () => {
    cy.mount(PlantabiliteLegend)
    cy.contains("Non plantable")
    cy.contains("Plantable")
  })
})
