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
  })

  it("should render the info button", () => {
    cy.get('button[aria-label="Informations"]').should("be.visible")
  })

  it("should show attribution popover when clicking info button", () => {
    cy.get('button[aria-label="Informations"]').click()
    cy.get('[data-cy="attribution-popover"]').should("exist")
    cy.get('[data-cy="attribution-popover"]').should("contain", "habitants")
    cy.get('[data-cy="attribution-popover"]').should("contain", "superficie")
  })

  it("should close popover when clicking outside", () => {
    cy.get('button[aria-label="Informations"]').click()
    cy.get('[data-cy="attribution-popover"]').should("exist")
    cy.get("body").click(0, 0)
    cy.get('[data-cy="attribution-popover"]').should("not.exist")
  })
})
