import MapScorePopup from "@/components/map/MapScorePopup.vue"

describe("Component:MapScorePopup", () => {
  it("renders correctly", () => {
    cy.mount(MapScorePopup, {
      props: {
        score: 8,
        lat: 45.75773479280862,
        lng: 4.8537684279176645
      }
    })
  })
})
