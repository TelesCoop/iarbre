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
    it("should filter tiles when clicking on plantability score labels", () => {
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

  describe("Climate Zones Legend Filtering", () => {
    beforeEach(() => {
      // Switch to climate zones layer
      cy.mapSwitchLayer(DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES])
      cy.getBySel("climate-zones-legend").should("be.visible")
    })

    it("should filter tiles when clicking on climate zone colors", () => {
      // Click on a zone color (zone 1)
      cy.getBySel("climate-zones-legend").find('[data-zone="1"]').should("be.visible").click()

      // Verify the zone has the selected visual state
      cy.getBySel("climate-zones-legend").find('[data-zone="1"]').should("have.class", "ring-2")

      // Click on another zone (zone A)
      cy.getBySel("climate-zones-legend").find('[data-zone="A"]').should("be.visible").click()

      // Verify both zones are selected
      cy.getBySel("climate-zones-legend").find('[data-zone="1"]').should("have.class", "ring-2")

      cy.getBySel("climate-zones-legend").find('[data-zone="A"]').should("have.class", "ring-2")

      // Test the expanded view
      cy.getBySel("climate-zones-legend").contains("Afficher les détails").click()

      // Click on zone in expanded view should also work
      cy.getBySel("climate-zones-legend").find('[data-zone="2"]').first().click()

      cy.getBySel("climate-zones-legend").find('[data-zone="2"]').should("have.class", "ring-2")
    })
  })

  describe("Vulnerability Legend Filtering", () => {
    beforeEach(() => {
      // Switch to vulnerability layer
      cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
      cy.getBySel("vulnerability-zones-legend").should("be.visible")
    })

    it("should filter tiles when clicking on vulnerability levels", () => {
      // Click on vulnerability level 1 (first level)
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="1"]')
        .should("be.visible")
        .click()

      // Verify the level has the selected visual state
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="1"]')
        .should("have.class", "ring-2")

      // Click on vulnerability level 5 (middle level)
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="5"]')
        .should("be.visible")
        .click()

      // Verify both levels are selected
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="1"]')
        .should("have.class", "ring-2")

      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="5"]')
        .should("have.class", "ring-2")

      // Click on level 9 (highest level)
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="9"]')
        .should("be.visible")
        .click()

      // Verify all three levels are selected
      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="1"]')
        .should("have.class", "ring-2")

      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="5"]')
        .should("have.class", "ring-2")

      cy.getBySel("vulnerability-zones-legend")
        .find('[data-vulnerability="9"]')
        .should("have.class", "ring-2")
    })
  })

  describe("Filter Persistence and Clearing", () => {
    it("should clear filters when switching between data types", () => {
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
    it("should show filter status when filters are active", () => {
      // Initially no filter status should be visible
      cy.getBySel("map-filters-status").should("not.exist")

      // Apply a plantability filter
      cy.getBySel("plantability-legend").find('[data-score="8"]').click()

      // Filter status should now be visible
      cy.getBySel("map-filters-status").should("be.visible")
      cy.getBySel("map-filters-status").should("contain", "Filtres actifs")
      cy.getBySel("map-filters-status").should("contain", "1 score")

      // Add another filter
      cy.getBySel("plantability-legend").find('[data-score="10"]').click()

      // Status should update
      cy.getBySel("map-filters-status").should("contain", "2 scores")

      // Test reset button
      cy.getBySel("reset-filters-button").should("be.visible").click()

      // All filters should be cleared
      cy.getBySel("map-filters-status").should("not.exist")
      cy.getBySel("plantability-legend").find('[data-score="8"]').should("not.have.class", "ring-2")
      cy.getBySel("plantability-legend")
        .find('[data-score="10"]')
        .should("not.have.class", "ring-2")
    })

    it("should show combined filter status for multiple data types", () => {
      // Apply plantability filter
      cy.getBySel("plantability-legend").find('[data-score="6"]').click()

      // Switch to vulnerability and apply filter
      cy.mapSwitchLayer(DataTypeToLabel[DataType.VULNERABILITY])
      cy.getBySel("vulnerability-zones-legend").find('[data-vulnerability="3"]').click()

      // Switch to climate zones and apply filter
      cy.mapSwitchLayer(DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES])
      cy.getBySel("climate-zones-legend").find('[data-zone="A"]').click()

      // Status should show combined count (but only active for current data type)
      cy.getBySel("map-filters-status").should("be.visible")
      cy.getBySel("map-filters-status").should("contain", "1 zone")

      // Reset should clear all filters
      cy.getBySel("reset-filters-button").click()
      cy.getBySel("map-filters-status").should("not.exist")
    })
  })
})
