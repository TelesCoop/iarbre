import MapSidePanelDownload from "@/components/map/panels/sidepanel/MapSidePanelDownload.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

describe("MapSidePanelDownload", () => {
  beforeEach(() => {
    cy.mount(MapSidePanelDownload)
  })

  it("should render the component with correct content", () => {
    cy.contains("Collectivités, aménageurs, urbanistes").should("be.visible")
    cy.contains("Demandez les données pour ce calque").should("be.visible")
    cy.get('[data-cy="download-data"]').should("be.visible")
    cy.contains("Obtenir les données").should("be.visible")
  })

  it("should open correct download link for PLANTABILITY data type", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.selectedDataType = DataType.PLANTABILITY
    })

    cy.window().then((win) => {
      cy.stub(win, "open").as("windowOpen")
    })

    cy.get('[data-cy="download-data"]').click()

    cy.get("@windowOpen").should(
      "have.been.calledWith",
      "https://data.grandlyon.com/portail/en/jeux-de-donnees/calque-plantabilite-metropole-lyon/info",
      "_blank"
    )
  })

  it("should open correct download link for CLIMATE_ZONE data type", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.selectedDataType = DataType.CLIMATE_ZONE
    })

    cy.window().then((win) => {
      cy.stub(win, "open").as("windowOpen")
    })

    cy.get('[data-cy="download-data"]').click()

    cy.get("@windowOpen").should(
      "have.been.calledWith",
      "https://www.data.gouv.fr/datasets/cartographie-des-zones-climatiques-locales-lcz-des-88-aires-urbaines-de-plus-de-50-000-habitants-de-france-metropolitaine/#/resources/e0c0f5e4-c8bb-4d33-aec9-ba16b5736102",
      "_blank"
    )
  })

  it("should open correct download link for VULNERABILITY data type", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.selectedDataType = DataType.VULNERABILITY
    })

    cy.window().then((win) => {
      cy.stub(win, "open").as("windowOpen")
    })

    cy.get('[data-cy="download-data"]').click()

    cy.get("@windowOpen").should(
      "have.been.calledWith",
      "https://data.grandlyon.com/portail/en/jeux-de-donnees/exposition-et-vulnerabilite-aux-fortes-chaleurs-dans-la-metropole-de-lyon/info",
      "_blank"
    )
  })

  it("should have arrow icon in the button", () => {
    cy.get('[data-cy="download-data"] svg').should("be.visible")
    cy.get('[data-cy="download-data"] svg path').should("have.attr", "stroke", "#426A45")
  })
})
