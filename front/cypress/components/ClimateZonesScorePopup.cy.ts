import ClimateZoneScorePopup from "@/components/map/popup/ClimateZoneScorePopup.vue"

describe("Component:ClimateZoneScorePopup", () => {
  it("renders correctly", () => {
    cy.mount(ClimateZoneScorePopup, {
      props: {
        index: 1,
        lat: 45.75773479280862,
        lng: 4.8537684279176645
      }
    })

    cy.contains("LCZ 1")
    cy.contains("Ensemble compact de tours")
  })
})
