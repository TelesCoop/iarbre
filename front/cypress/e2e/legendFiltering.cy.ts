import { DataType, DataTypeToLabel } from "../../src/utils/enum"

describe("Legend Filtering", () => {
  beforeEach(() => {
    cy.visit("/plantability/13/45.07126/5.5543")
    cy.get("@consoleInfo").should("have.been.calledWith", "cypress: map data Plan loaded")
    cy.get("@consoleInfo").should(
      "have.been.calledWith",
      "cypress: layer: tile-plantability-layer and source: tile-plantability-source loaded."
    )
    cy.wait(150) // eslint-disable-line cypress/no-unnecessary-waiting
  })

  describe("Plantability Legend Filtering", () => {
    it("filter tiles when clicking on plantability score labels", () => {
      // Verify plantability legend is visible
      cy.getBySel("plantability-legend").should("be.visible")

      // Click on score 8 in the legend to filter
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("be.visible").click()

      // Verify the score label has the selected visual state (ring)
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("have.class", "ring-2")

      // Click on score 10 to add another filter
      cy.getBySel("plantability-legend").find('[data-score="10"]').should("be.visible").click()

      // Verify both scores are now selected
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("have.class", "ring-2")

      cy.getBySel("plantability-legend").find('[data-score="10"]').should("have.class", "ring-2")

      // Click on score 8 again to deselect it
      cy.getBySel("plantability-legend").find('[data-score="8"]').click()

      // Verify score 8 is no longer selected but score 10 still is
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("not.have.class", "ring-2")

      cy.getBySel("plantability-legend").find('[data-score="10"]').should("have.class", "ring-2")
    })
  })

  describe("Filter Persistence and Clearing", () => {
    it("clear filters when switching between data types", () => {
      // Start with plantability and set a filter
      cy.getBySel("plantability-legend").find('[data-score="6"]').click()

      cy.getBySel("plantability-legend").find('[data-score="6"]').should("have.class", "ring-2")

      // Switch to vulnerability
      cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])

      // Switch back to plantability
      cy.mapSwitchLayer(DataTypeToLabel[DataType.PLANTABILITY])

      // Verify the filter has been cleared
      cy.getBySel("plantability-legend").find('[data-score="6"]').should("not.have.class", "ring-2")
    })
  })

  describe("Filter Status and Reset", () => {
    it("show filter status when filters are active", () => {
      // Initially no filter status be visible
      cy.getBySel("map-filters-status").should("not.exist")

      // Apply a plantability filter
      cy.getBySel("plantability-legend").find('[data-score="8"]').click()

      // Filter status now be visible
      cy.getBySel("map-filters-status").should("be.visible")
      cy.getBySel("filter-summary").should("contain", "1\u00A0score")

      // Add another filter
      cy.getBySel("plantability-legend").find('[data-score="10"]').click()

      // Status update
      cy.getBySel("filter-summary").should("contain", "2\u00A0scores")

      // Test reset button
      cy.getBySel("reset-filters-button").should("be.visible").click()

      // All filters be cleared
      cy.getBySel("map-filters-status").should("not.exist")
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("not.have.class", "ring-2")
      cy.getBySel("plantability-legend")
        .find('[data-score="10"]')
        .should("not.have.class", "ring-2")
    })
  })

  describe("Filter Status Component", () => {
    it("show correct filter labels and styling", () => {
      // Test plantability filter labels
      cy.getBySel("plantability-legend").find('[data-score="6"]').click()
      cy.getBySel("filter-summary").should("contain", "1\u00A0score")

      cy.getBySel("plantability-legend").find('[data-score="8"]').click()
      cy.getBySel("filter-summary").should("contain", "2\u00A0scores")

      // Check component structure and accessibility
      cy.getBySel("map-filters-status").should("be.visible")
      cy.getBySel("map-filters-status").should("contain", "Filtres")
      cy.getBySel("reset-filters-button")
        .should("be.visible")
        .should("have.attr", "title", "Supprimer tous les filtres")
    })
  })
})
