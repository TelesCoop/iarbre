import MapSidePanelDownload from "@/components/map/panels/sidepanel/MapSidePanelDownload.vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToDownloadLink } from "@/utils/enum"

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
      DataTypeToDownloadLink[DataType.PLANTABILITY],
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
      DataTypeToDownloadLink[DataType.CLIMATE_ZONE],
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
      DataTypeToDownloadLink[DataType.VULNERABILITY],
      "_blank"
    )
  })

  it("should open correct download link for PLANTABILITY_VULNERABILITY data type", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.selectedDataType = DataType.PLANTABILITY_VULNERABILITY
    })

    cy.window().then((win) => {
      cy.stub(win, "open").as("windowOpen")
    })

    cy.get('[data-cy="download-data"]').click()

    cy.get("@windowOpen").should(
      "have.been.calledWith",
      DataTypeToDownloadLink[DataType.PLANTABILITY_VULNERABILITY],
      "_blank"
    )
  })

  it("should open correct download link for VEGETATION data type", () => {
    cy.window().then(() => {
      const store = useMapStore()
      store.selectedDataType = DataType.VEGETATION
    })

    cy.window().then((win) => {
      cy.stub(win, "open").as("windowOpen")
    })

    cy.get('[data-cy="download-data"]').click()

    cy.get("@windowOpen").should(
      "have.been.calledWith",
      DataTypeToDownloadLink[DataType.VEGETATION],
      "_blank"
    )
  })

  it("should have arrow icon in the button", () => {
    cy.get('[data-cy="download-data"] svg').should("be.visible")
    cy.get('[data-cy="download-data"] svg path').should("have.attr", "stroke", "#426A45")
  })
})
