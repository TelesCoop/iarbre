import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapSidePanel from "@/components/map/panels/sidepanel/MapSidePanel.vue"
import PrimeVue from "primevue/config"
import ToastService from "primevue/toastservice"

describe("MapSidePanel", () => {
  beforeEach(() => {
    const pinia = createPinia()

    mount(MapSidePanel, {
      global: {
        plugins: [pinia, PrimeVue, ToastService]
      }
    })
  })

  it("should include all sub-components", () => {
    cy.get('[data-cy="map-side-panel-header"]').should("exist")
    cy.contains("QPV").should("be.visible")
    cy.get('[data-cy="map-layer-switcher"]').should("exist")
    cy.get('[data-cy="map-context-data"]').should("exist")
    cy.get('[data-cy="map-side-panel-download"]').should("exist")
    cy.get('[data-cy="map-side-panel-footer"]').should("exist")
  })
})
