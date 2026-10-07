/// <reference types="cypress" />
import { MOBILE_VIEWPORT } from "../support/viewports"

const NARROW_DESKTOP_VIEWPORT = { width: 1024, height: 768 }
/** `--map-edge-gap`, the gap between map overlays and the edges they sit against. */
const EDGE_GAP_PX = 8

const rectOf = (selector: string) =>
  cy
    .get(selector)
    .filter(":visible")
    .first()
    .then(($el) => $el[0].getBoundingClientRect())

const setMapState = (state: Record<string, unknown>) =>
  cy.mapStore().then((store) => Object.assign(store, state))

const selectParcel = () =>
  setMapState({
    selectedCadastreParcel: { parcelId: "1", section: "AB", numero: "12", surface: 345 }
  })

const openStreetView = () =>
  setMapState({
    selectedPanoramaxPicture: {
      id: "picture",
      type: "flat",
      assets: { sd: "/images/satellite.png" }
    }
  })

// cy.click() fails when another element covers its target: each click below checks an overlap.
const closeParcelCard = () => cy.get("[data-cy=cadastre-parcel-info] [aria-label=Fermer]").click()

describe("Map layout - Desktop", () => {
  beforeEach(() => cy.visitMap(NARROW_DESKTOP_VIEWPORT))

  it("keeps the street view clear of the legend and of the map controls", () => {
    openStreetView()

    rectOf(".legend-container").then((legend) => {
      rectOf("[data-cy=panoramax-viewer]").then((viewer) => {
        expect(viewer.left).to.be.at.least(legend.right)
      })
    })
    cy.get(".maplibregl-ctrl-center").click()
  })

  it("keeps the parcel card clear of the layer toggles", () => {
    selectParcel()

    cy.getBySel("qpv-toggle").filter(":visible").click()
    closeParcelCard()
  })
})

describe("Map layout - Mobile", () => {
  beforeEach(() => cy.visitMap(MOBILE_VIEWPORT))

  it("keeps the bottom controls just above the details panel", () => {
    rectOf("[data-cy=mobile-panel-handle]").then((handle) => {
      rectOf(".maplibregl-ctrl-3d").then((control) => {
        expect(handle.top - control.bottom).to.equal(EDGE_GAP_PX)
      })
    })
  })

  it("keeps the parcel card above the details panel", () => {
    selectParcel()

    closeParcelCard()
  })

  it("opens the draw panel under the legend and above a selected parcel card", () => {
    selectParcel()
    cy.getBySel("shape-toolbar-toggle").click()

    cy.getBySel("shape-mode-polygon").click()
    rectOf(".legend-container").then((legend) => {
      rectOf("[data-cy=shape-toolbar]").then((panel) => {
        expect(panel.top).to.be.at.least(legend.bottom)
      })
    })
  })

  it("keeps the finished-shape panel under the legend", () => {
    cy.mapStore().then((store) => {
      store.enterShapeMode("polygon")
      store.markShapeFinished()
    })

    cy.getBySel("zone-dashboard-cta").should("be.visible")
    rectOf(".legend-container").then((legend) => {
      rectOf("[data-cy=shape-toolbar]").then((panel) => {
        expect(panel.top).to.be.at.least(legend.bottom)
      })
    })
  })

  it("keeps the street view above the map controls", () => {
    openStreetView()

    cy.get(".maplibregl-ctrl-center").click()
  })

  it("keeps the layer toggles inside the screen when the details panel is open", () => {
    cy.getBySel("mobile-panel-handle").click()

    cy.get("[data-cy=mobile-panel] .layer-chip").each(($chip) => {
      const { left, right } = $chip[0].getBoundingClientRect()
      expect(left).to.be.at.least(0)
      expect(right).to.be.at.most(MOBILE_VIEWPORT.width)
    })
  })
})
