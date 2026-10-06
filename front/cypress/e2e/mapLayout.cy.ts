/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const MOBILE_VIEWPORT = { width: 375, height: 667 }
const DESKTOP_VIEWPORT = { width: 1440, height: 900 }
const SHORT_DESKTOP_VIEWPORT = { width: 1280, height: 620 }
/** `--map-edge-gap`, the gap between map overlays and the edges they sit against. */
const EDGE_GAP_PX = 8

const rectOf = (selector: string) =>
  cy
    .get(selector)
    .filter(":visible")
    .first()
    .then(($el) => $el[0].getBoundingClientRect())

const visitMap = (viewport: { width: number; height: number }) => {
  cy.viewport(viewport.width, viewport.height)
  LocalStorageHandler.setItem("hasVisitedBefore", true)
  cy.visit("/plantability/13/45.07126/5.55430")
  cy.get("@consoleInfo").should(
    "have.been.calledWith",
    "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
  )
}

const rectsOverlap = (a: DOMRect, b: DOMRect) =>
  a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom

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

const expectStreetViewAboveMapControls = () =>
  rectOf(".maplibregl-ctrl-center").then((topControl) => {
    rectOf("[data-cy=panoramax-viewer]").then((viewer) => {
      expect(viewer.bottom).to.be.at.most(topControl.top)
    })
  })

describe("Map layout - Desktop", () => {
  beforeEach(() => visitMap(DESKTOP_VIEWPORT))

  it("keeps the map controls at the same distance from the edges as the other overlays", () => {
    rectOf("[data-cy=map-component]").then((map) => {
      rectOf(".maplibregl-ctrl-3d").then((control) => {
        expect(map.right - control.right).to.equal(EDGE_GAP_PX)
        expect(map.bottom - control.bottom).to.equal(EDGE_GAP_PX)
      })
      rectOf("[data-cy=bottom-left-controls]").then((bottomLeft) => {
        expect(map.bottom - bottomLeft.bottom).to.equal(EDGE_GAP_PX)
      })
    })
  })
  it("keeps the parcel card above the layer toggles", () => {
    selectParcel()

    rectOf("[data-cy=bottom-left-controls] .layer-toggles").then((toggles) => {
      rectOf("[data-cy=cadastre-parcel-info]").then((card) => {
        expect(card.bottom).to.be.at.most(toggles.top)
      })
    })
  })
})

describe("Map layout - Short desktop", () => {
  beforeEach(() => visitMap(SHORT_DESKTOP_VIEWPORT))

  it("keeps the street view clear of the legend and of the map controls", () => {
    openStreetView()

    rectOf(".legend-container").then((legend) => {
      rectOf("[data-cy=panoramax-viewer]").then((viewer) => {
        expect(viewer.left).to.be.at.least(legend.right)
      })
    })
    expectStreetViewAboveMapControls()
  })
})

describe("Map layout - Mobile", () => {
  beforeEach(() => visitMap(MOBILE_VIEWPORT))

  it("keeps the bottom controls just above the details panel", () => {
    rectOf("[data-cy=mobile-panel-handle]").then((handle) => {
      rectOf(".maplibregl-ctrl-3d").then((control) => {
        expect(handle.top - control.bottom).to.equal(EDGE_GAP_PX)
      })
    })
  })

  it("keeps the expanded background selector clear of the draw trigger", () => {
    cy.getBySel("bg-selector-toggle").click()
    cy.get(".bg-selector-options img").each(($img) =>
      cy
        .wrap($img)
        .should(($loaded) => expect(($loaded[0] as HTMLImageElement).complete).to.equal(true))
    )
    cy.wait(400) // eslint-disable-line cypress/no-unnecessary-waiting

    rectOf("[data-cy=shape-toolbar-toggle]").then((trigger) => {
      rectOf(".bg-selector-container").then((selector) => {
        expect(selector.right).to.be.at.most(trigger.left)
      })
    })
  })

  it("keeps the parcel card above the details panel", () => {
    selectParcel()

    rectOf("[data-cy=mobile-panel-handle]").then((handle) => {
      rectOf("[data-cy=cadastre-parcel-info]").then((card) => {
        expect(card.bottom).to.be.at.most(handle.top)
      })
    })
  })

  it("keeps the draw panel clear of the legend and of the map controls", () => {
    cy.getBySel("shape-toolbar-toggle").click()

    rectOf("[data-cy=shape-toolbar]").then((panel) => {
      for (const selector of [".legend-container", ".maplibregl-ctrl-bottom-right"]) {
        rectOf(selector).then((other) => expect(rectsOverlap(panel, other)).to.equal(false))
      }
    })
  })

  it("keeps the street view above the map controls", () => {
    openStreetView()

    expectStreetViewAboveMapControls()
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
