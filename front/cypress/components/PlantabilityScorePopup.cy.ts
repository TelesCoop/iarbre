import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopup.vue"

describe("Component:PlantabilityScorePopup", () => {
  it("renders correctly", () => {
    cy.mount(PlantabilityScorePopup, {
      props: {
        index: 0.821,
        lat: 45.75773479280862,
        lng: 4.8537684279176645
      }
    })

    cy.contains("8/10")
    cy.contains("Plantabilité élevée")
  })
})
