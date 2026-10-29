/// <reference types="cypress" />
import {
  DataType,
  DataTypeToLabel,
  MapStyle,
  OverlayLayer,
  PublicBuildingCategory
} from "../../src/utils/enum"
import { GEOCODER_API_URL } from "../../src/utils/geocoder"
import { LocalStorageHandler } from "../../src/utils/LocalStorageHandler"
const MOBILE_VIEWPORT = { width: 375, height: 667 }
const DESKTOP_VIEWPORT = { width: 1440, height: 900 }
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

const showPublicBuildingsAndSelectSchool = () => {
  cy.getBySel("public-buildings-toggle").filter(":visible").should("be.visible").click()
  cy.mapCheckPublicBuildingsLayer(true)
  setMapState({
    selectedPublicBuilding: {
      id: 1,
      name: "École Élémentaire Jean Jaurès",
      category: PublicBuildingCategory.ENSEIGNEMENT,
      nature: "Enseignement primaire",
      natureDetaillee: "Ecole élémentaire",
      studentCount: 250,
      educationPriority: "REP+",
      capacity: null
    }
  })
}

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

const expectBackgroundSelectorExpanded = (isExpanded: boolean) =>
  cy.getBySel("bg-selector-toggle").should("have.attr", "aria-expanded", String(isExpanded))

/** A spot of the mobile map that no overlay covers: right column, below the search bar. */
const tapMap = () => cy.getBySel("map-component").click(270, 200)

const expectLayerBelow = (lowerLayerId: string, upperLayerId: string) =>
  cy.mapStore().should((store) => {
    const layersOrder: string[] = store.mapInstancesByIds.default.getLayersOrder()
    expect(layersOrder).to.include.members([lowerLayerId, upperLayerId])
    expect(layersOrder.indexOf(lowerLayerId)).to.be.lessThan(layersOrder.indexOf(upperLayerId))
  })

describe("Map - Desktop", () => {
  beforeEach(() => {
    cy.visitMap(DESKTOP_VIEWPORT)
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data osm loaded")
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("loads with plantability layer", () => {
    cy.getBySel("plantability-legend").should("exist")
    cy.getBySel("map-component").should("exist")
  })

  it("changes map style via background selector", () => {
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.get("@consoleInfo").should("not.have.been.calledWith", "cypress: QPV data loaded") // #344

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("changes to orthophoto map style", () => {
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.ORTHOPHOTO}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("switches data layer via sidebar", () => {
    // Desktop uses sidebar layer switcher (filter visible to exclude mobile hidden elements)
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
  })

  it("shows plantability context data", () => {
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Zoomez et cliquez sur un carreau")
    cy.mapZoomTo(3)
    cy.getBySel("map-component").click("center")
  })

  it("shows vulnerability context data", () => {
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()

    cy.getBySel("map-context-data").should("contain", "Cliquez sur une zone")
  })

  it("shows climate zone context data", () => {
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.CLIMATE_ZONE]).click()
    cy.getBySel("map-context-data").should("exist")
    cy.getBySel("map-context-data").should("contain", "Cliquez sur un carreau")
  })

  it("renders layer toggle buttons in the bottom-left controls", () => {
    cy.getBySel("bottom-left-controls").should("be.visible")

    // The three layer chips must live inside the bottom-left stack,
    // stacked below the background selector.
    cy.getBySel("bottom-left-controls").within(() => {
      cy.getBySel("bg-selector-toggle").should("be.visible")
      cy.getBySel("qpv-toggle").should("be.visible").and("contain.text", "QPV")
      cy.getBySel("cadastre-toggle").should("be.visible").and("contain.text", "Cadastre")
      cy.getBySel("boundary-toggle").should("be.visible").and("contain.text", "Communes")
    })

    // Positioned in the bottom-left quadrant of the viewport.
    cy.getBySel("bottom-left-controls").then(($el) => {
      const rect = $el[0].getBoundingClientRect()
      expect(rect.left).to.be.lessThan(DESKTOP_VIEWPORT.width / 2)
      expect(rect.bottom).to.be.greaterThan(DESKTOP_VIEWPORT.height / 2)
    })
  })

  it("adds QPV layer when toggled", () => {
    // Desktop QPV toggle is in the sidebar
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(false)
  })

  it("maintains QPV layer when switching data layers", () => {
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.CLIMATE_ZONE]).click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
    cy.mapCheckQPVLayer(true)
  })

  it("keeps the QPV borders above the data layer when switching 2D/3D", () => {
    cy.getBySel("qpv-toggle").filter(":visible").click()
    cy.mapCheckQPVLayer(true)

    cy.get(".maplibregl-ctrl-3d").click()
    expectLayerBelow("tile-plantability-layer", "qpv-border-casing")

    cy.get(".maplibregl-ctrl-3d").click()
    expectLayerBelow("tile-plantability-layer", "qpv-border-casing")
  })

  it("maintains QPV layer when switching basemap styles", () => {
    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.mapCheckQPVLayer(true)
  })

  it("adds cadastre layer when toggled", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
  })

  it("maintains cadastre layer when switching data layers", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.PLANTABILITY]).click()
    cy.mapCheckCadastreLayer(true)
  })

  it("maintains cadastre layer when switching basemap styles", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.OSM}"]`).should("be.visible").click()
    cy.mapCheckCadastreLayer(true)
  })

  it("displays cadastre layer at max zoom level", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    // Zoom from 13 to 18 (max zoom)
    cy.mapZoomTo(5)
    cy.mapCheckCadastreLayer(true)
  })

  it("hides cadastre parcel info when layer is toggled off", () => {
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)
    cy.getBySel("cadastre-parcel-info").should("not.exist")

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
    cy.getBySel("cadastre-parcel-info").should("not.exist")
  })

  it("adds panoramax layer when toggled, off by default", () => {
    cy.getBySel("panoramax-credit").should("not.exist")
    cy.getBySel("panoramax-viewer").should("not.exist")

    cy.getBySel("panoramax-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPanoramaxLayer(true)
    cy.getBySel("panoramax-credit").should("be.visible")
    cy.getBySel("panoramax-viewer").should("not.exist")

    cy.getBySel("panoramax-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPanoramaxLayer(false)
    cy.getBySel("panoramax-credit").should("not.exist")
  })

  it("zooms in to the picture level when panoramax is activated", () => {
    cy.url().should("include", "/13/")

    cy.getBySel("panoramax-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPanoramaxLayer(true)

    cy.url().should("include", "/17/")
  })

  it("maintains panoramax layer when switching data layers and basemap styles", () => {
    cy.getBySel("panoramax-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPanoramaxLayer(true)

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckPanoramaxLayer(true)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.mapCheckPanoramaxLayer(true)
  })

  it("adds public buildings layer when toggled", () => {
    cy.getBySel("public-buildings-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPublicBuildingsLayer(true)

    cy.getBySel("public-buildings-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPublicBuildingsLayer(false)
  })

  it("shows the selected public building card until it is closed", () => {
    showPublicBuildingsAndSelectSchool()

    cy.getBySel("public-building-info")
      .should("contain.text", "École Élémentaire Jean Jaurès")
      .and("contain.text", "Ecole élémentaire")
      .and("contain.text", "250")
      .and("contain.text", "REP+")
      .and("not.contain.text", "Places d'accueil")

    cy.get("[data-cy=public-building-info] [aria-label=Fermer]").click()
    cy.getBySel("public-building-info").should("not.exist")
  })

  it("keeps the selected public building when switching data layers", () => {
    showPublicBuildingsAndSelectSchool()

    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
    cy.mapCheckPublicBuildingsLayer(true)
    cy.getBySel("public-building-info").should("be.visible")
  })

  it("clears the selected public building when its category is unchecked", () => {
    showPublicBuildingsAndSelectSchool()
    cy.getBySel("public-building-info").should("be.visible")

    cy.getBySel("public-buildings-categories-toggle").filter(":visible").click()
    cy.get('[data-cy="public-buildings-category-enseignement"] input').uncheck()
    cy.getBySel("public-building-info").should("not.exist")
  })

  it("writes the filtered public building categories in the URL", () => {
    cy.getBySel("public-buildings-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckPublicBuildingsLayer(true)

    cy.getBySel("public-buildings-categories-toggle").filter(":visible").click()
    cy.get('[data-cy="public-buildings-category-enseignement"] input').uncheck()
    cy.location("search").should(
      "eq",
      `?layers=${OverlayLayer.PUBLIC_BUILDINGS}&buildings=petite_enfance,sante,administratif,culture`
    )

    cy.get('[data-cy="public-buildings-category-enseignement"] input').check()
    cy.location("search").should("eq", `?layers=${OverlayLayer.PUBLIC_BUILDINGS}`)
  })

  it("writes the basemap and the overlay layers in the URL", () => {
    cy.location("search").should("eq", "")

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.location("search").should("eq", `?layers=${OverlayLayer.QPV}`)

    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.location("search").should("eq", `?basemap=${MapStyle.SATELLITE}&layers=${OverlayLayer.QPV}`)

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.location("search").should("eq", `?basemap=${MapStyle.SATELLITE}`)
  })

  it("keeps the basemap and the overlay layers when coming back from the dashboard", () => {
    cy.intercept("GET", "**/api/dashboard/", { fixture: "dashboard.json" })
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.get(`[data-cy="bg-option-${MapStyle.SATELLITE}"]`).should("be.visible").click()
    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("dashboard-button").click()
    cy.location("pathname").should("eq", "/dashboard")
    cy.get(".back-to-map").click()

    cy.location("search").should(
      "eq",
      `?basemap=${MapStyle.SATELLITE}&layers=${OverlayLayer.CADASTRE}`
    )
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      `cypress: map data ${MapStyle.SATELLITE} loaded`
    )
    cy.getBySel("cadastre-toggle").filter(":visible").should("have.class", "active")
  })

  it("fits the street view and the parcel card on a 1024px wide screen", () => {
    cy.viewport(NARROW_DESKTOP_VIEWPORT.width, NARROW_DESKTOP_VIEWPORT.height)
    openStreetView()

    rectOf(".legend-container").then((legend) => {
      rectOf("[data-cy=panoramax-viewer]").then((viewer) => {
        expect(viewer.left).to.be.at.least(legend.right)
      })
    })
    cy.get(".maplibregl-ctrl-center").click()

    selectParcel()
    cy.getBySel("qpv-toggle").filter(":visible").click()
    closeParcelCard()
  })

  it("keeps the background selector open while the map is dragged", () => {
    cy.getBySel("bg-selector-toggle").click()

    cy.getBySel("map-component").trigger("pointerdown", 700, 300)
    cy.getBySel("map-component").trigger("click", 800, 400)

    expectBackgroundSelectorExpanded(true)
  })
})

describe("Map - Shared link", () => {
  beforeEach(() => {
    cy.visitMap(
      DESKTOP_VIEWPORT,
      `/plantability/13/45.07126/5.55430?basemap=${MapStyle.SATELLITE}&layers=${OverlayLayer.QPV},${OverlayLayer.CADASTRE}`
    )
  })

  it("restores the basemap from the URL", () => {
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      `cypress: map data ${MapStyle.SATELLITE} loaded`
    )
  })

  it("restores the overlay layers from the URL", () => {
    cy.mapCheckQPVLayer(true)
    cy.mapCheckCadastreLayer(true)
    cy.getBySel("qpv-toggle").filter(":visible").should("have.class", "active")
    cy.getBySel("cadastre-toggle").filter(":visible").should("have.class", "active")
    cy.getBySel("boundary-toggle").filter(":visible").should("not.have.class", "active")
  })

  it("keeps the shared display in the URL", () => {
    cy.mapCheckQPVLayer(true)
    cy.location("search").should(
      "eq",
      `?basemap=${MapStyle.SATELLITE}&layers=${OverlayLayer.QPV},${OverlayLayer.CADASTRE}`
    )
  })
})

describe("Map - Mobile", () => {
  beforeEach(() => {
    cy.visitMap(MOBILE_VIEWPORT)
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data osm loaded")
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("loads map on mobile viewport, its controls just above the details panel", () => {
    cy.getBySel("map-component").should("exist")
    rectOf("[data-cy=mobile-panel-handle]").then((handle) => {
      rectOf(".maplibregl-ctrl-3d").then((control) => {
        expect(handle.top - control.bottom).to.equal(EDGE_GAP_PX)
      })
    })
  })

  it("switches data layer on mobile via layer switcher", () => {
    cy.getBySel("mobile-layer-switcher").should("be.visible")
    cy.getBySel("layer-switcher").filter(":visible").should("be.visible").click()
    cy.get(".select-option-label").contains(DataTypeToLabel[DataType.VULNERABILITY]).click()
  })

  it("toggles QPV layer on mobile", () => {
    // Open mobile panel to access toggles
    cy.getBySel("mobile-panel-handle").should("be.visible").click()
    cy.get("[data-cy=mobile-panel] .layer-chip").each(($chip) => {
      const { left, right } = $chip[0].getBoundingClientRect()
      expect(left).to.be.at.least(0)
      expect(right).to.be.at.most(MOBILE_VIEWPORT.width)
    })

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(true)

    cy.getBySel("qpv-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckQPVLayer(false)
  })

  it("toggles cadastre layer on mobile", () => {
    cy.getBySel("mobile-panel-handle").should("be.visible").click()

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(true)

    cy.getBySel("cadastre-toggle").filter(":visible").should("be.visible").click()
    cy.mapCheckCadastreLayer(false)
  })

  it("changes map style on mobile via background selector", () => {
    cy.getBySel("bg-selector-toggle").should("be.visible").click()
    cy.getBySel("bg-option-satellite").should("be.visible").click()

    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
  })

  it("stacks the parcel card and the shape panel above the details panel, under the legend", () => {
    const expectShapePanelUnderLegend = () =>
      rectOf(".legend-container").then((legend) => {
        rectOf("[data-cy=shape-toolbar]").then((panel) => {
          expect(panel.top).to.be.at.least(legend.bottom)
        })
      })

    selectParcel()
    closeParcelCard()

    selectParcel()
    cy.getBySel("shape-toolbar-toggle").click()
    cy.getBySel("shape-mode-polygon").click()
    expectShapePanelUnderLegend()

    cy.mapStore().then((store) => store.markShapeFinished())
    cy.getBySel("zone-dashboard-cta").should("be.visible")
    expectShapePanelUnderLegend()
  })

  it("keeps the street view above the map controls", () => {
    openStreetView()

    cy.get(".maplibregl-ctrl-center").click()
  })

  it("folds the background selector and the shape panel when the user moves on", () => {
    cy.getBySel("bg-selector-toggle").click()
    expectBackgroundSelectorExpanded(true)
    tapMap()
    expectBackgroundSelectorExpanded(false)

    cy.getBySel("bg-selector-toggle").click()
    cy.getBySel("shape-toolbar-toggle").click()
    expectBackgroundSelectorExpanded(false)

    cy.get("[data-cy='map-geocoder'] input").trigger("keydown", { key: "Escape" })
    cy.getBySel("shape-toolbar").should("be.visible")
    cy.getBySel("shape-toolbar-toggle").trigger("keydown", { key: "Escape" })
    cy.getBySel("shape-toolbar").should("not.exist")

    cy.getBySel("shape-toolbar-toggle").click()
    tapMap()
    cy.getBySel("shape-toolbar").should("not.exist")
  })

  it("keeps the shape panel open while drawing, until the background selector opens", () => {
    cy.getBySel("shape-toolbar-toggle").click()
    cy.getBySel("shape-mode-polygon").click()
    tapMap()
    cy.getBySel("shape-toolbar").should("be.visible")

    cy.getBySel("bg-selector-toggle").click()
    cy.getBySel("shape-toolbar").should("not.exist")
    expectBackgroundSelectorExpanded(true)
  })
})

describe("Geocoder", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data osm loaded")
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("search for an address in Lyon and display results", () => {
    cy.intercept("GET", `${GEOCODER_API_URL}*`).as("geocoding")
    cy.get("[data-cy='map-geocoder'] input", { timeout: 10000 }).should("be.visible").click()
    cy.get("[data-cy='map-geocoder'] input").type("Métropole de Lyon")
    cy.wait("@geocoding")
    cy.get("[data-cy='map-geocoder'] ul[role='listbox']").should("be.visible")
    cy.get("[data-cy='map-geocoder'] li[role='option']").should("have.length.at.least", 1)
  })
})

describe("Map - Biosphere functional integrity", () => {
  beforeEach(() => {
    LocalStorageHandler.setItem("hasVisitedBefore", true)
    cy.visit(`/${DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY}/13/45.07126/5.55430`)
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data osm loaded")
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  it("shows biosphere empty message before clicking", () => {
    cy.getBySel("map-context-data").should("contain", "Cliquez sur une zone.")
  })
})

describe("Welcome message", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.55430")
  })

  it("Close when clicked and don't show up again", () => {
    cy.getBySel("welcome-dialog").should("be.visible")
    cy.getBySel("welcome-click").should("be.visible").click()
    cy.getBySel("welcome-dialog").should("not.exist")
    cy.visit("/plantability/13/45.07126/5.55430")
    cy.getBySel("welcome-dialog").should("not.exist")
  })
})
