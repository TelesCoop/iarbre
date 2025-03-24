import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopup.vue"

describe("Component:PlantabilityScorePopup", () => {
  it("renders correctly", () => {
    cy.mount(PlantabilityScorePopup, {
      props: {
        index: 0.821
      }
    })

    cy.contains("8/10")
    cy.contains("Plantabilité élevée")
  })
})
