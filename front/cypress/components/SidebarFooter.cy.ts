import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import MapSidePanelFooter from "@/components/map/panels/sidepanel/MapSidePanelFooter.vue"
import { useMapStore } from "@/stores/map"
import PrimeVue from "primevue/config"
import ToastService from "primevue/toastservice"

describe("MapSidePanelFooter", () => {
  beforeEach(() => {
    const pinia = createPinia()

    mount(MapSidePanelFooter, {
      global: {
        plugins: [pinia, PrimeVue, ToastService]
      }
    })
  })

  it("should render the component with correct content", () => {
    cy.contains("Coordonnées géographiques").should("be.visible")
    cy.get('[data-cy="copy-coords-button"]').should("be.visible")
  })

  it("should display coordinates in correct format", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.clickCoordinates = { lat: 45.12345, lng: 4.56789 }
    })

    cy.get('[data-cy="copy-coords-button"]').should("contain.text", "45.12345° N, 4.56789° E")
  })

  it("should copy coordinates to clipboard when button is clicked", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.clickCoordinates = { lat: 46.78901, lng: 2.34567 }
    })

    // Mock navigator.clipboard.writeText
    let clipboardContent = ""
    cy.window().then((win) => {
      cy.stub(win.navigator.clipboard, "writeText").callsFake((text) => {
        clipboardContent = text
        return Promise.resolve()
      })
    })

    cy.get('[data-cy="copy-coords-button"]').click()

    cy.then(() => {
      expect(clipboardContent).to.equal("46.78901° N, 2.34567° E")
    })
  })

  it("should update coordinates when map store coordinates change", () => {
    cy.window().then(() => {
      const store = useMapStore()
      // Initial coordinates
      store.clickCoordinates = { lat: 45.12345, lng: 4.56789 }
    })

    cy.get('[data-cy="copy-coords-button"]').should("contain.text", "45.12345° N, 4.56789° E")

    cy.window().then(() => {
      const store = useMapStore()
      // Change coordinates
      store.clickCoordinates = { lat: 46.54321, lng: 5.98765 }
    })

    cy.get('[data-cy="copy-coords-button"]').should("contain.text", "46.54321° N, 5.98765° E")
  })
})
