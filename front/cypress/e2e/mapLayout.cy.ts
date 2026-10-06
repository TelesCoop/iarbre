/// <reference types="cypress" />
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"

const MOBILE_VIEWPORT = { width: 375, height: 667 }
const DESKTOP_VIEWPORT = { width: 1440, height: 900 }
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

const selectParcel = () =>
  cy.window().then((win) => {
    const app = (win.document.querySelector("#app") as any).__vue_app__
    app.config.globalProperties.$pinia._s.get("map").selectedCadastreParcel = {
      parcelId: "1",
      section: "AB",
      numero: "12",
      surface: 345
    }
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

describe("Map layout - Mobile", () => {
  beforeEach(() => visitMap(MOBILE_VIEWPORT))

  it("keeps the bottom controls just above the details panel", () => {
    rectOf("[data-cy=mobile-panel-handle]").then((handle) => {
      rectOf(".maplibregl-ctrl-3d").then((control) => {
        expect(handle.top - control.bottom).to.equal(EDGE_GAP_PX)
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

  it("shows the draw panel above the legend", () => {
    cy.getBySel("shape-toolbar-toggle").click()

    cy.get(".shape-toolbar__panel button")
      .first()
      .then(($button) => {
        const { left, top, width, height } = $button[0].getBoundingClientRect()
        const topElement = $button[0].ownerDocument.elementFromPoint(
          left + width / 2,
          top + height / 2
        )
        expect($button[0].contains(topElement)).to.equal(true)
      })
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
