import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapSidePanelHeader from "@/components/map/panels/sidepanel/MapSidePanelHeader.vue"

describe("MapSidePanelHeader", () => {
  beforeEach(() => {
    const pinia = createPinia()

    mount(MapSidePanelHeader, {
      global: {
        plugins: [pinia]
      }
    })
  })

  it("should render the component with correct content", () => {
    cy.contains("Métropole de Lyon").should("be.visible")
    cy.contains("habitants").should("be.visible")
    cy.contains("superficie").should("be.visible")
  })
})
