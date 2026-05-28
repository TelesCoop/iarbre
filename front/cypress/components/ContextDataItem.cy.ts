import ContextDataFactorRow from "@/components/contextData/shared/ContextDataFactorRow.vue"
import type { ContextDataFactor, ContextDataVulnerabilityFactor } from "@/types/contextData"

describe("ContextDataFactorRow.vue", () => {
  const baseFactor: ContextDataFactor = {
    key: "test-factor",
    label: "Test Factor",
    value: "50",
    unit: "%",
    icon: "heat",
    impact: "positive",
    description: "Test description"
  }

  it("renders basic factor with all props", () => {
    cy.mount(ContextDataFactorRow, {
      props: {
        factor: baseFactor
      }
    })

    cy.contains("Test Factor").should("be.visible")
    cy.contains("50").should("be.visible")
    cy.contains("%").should("be.visible")
    cy.get('[data-cy="factor-test-factor"]').should("exist")
    cy.get(".impact-positive").should("exist")
  })

  it("renders vulnerability factor with day and night scores", () => {
    const vulnerabilityFactor: ContextDataVulnerabilityFactor = {
      ...baseFactor,
      factorId: "heat",
      dayScore: 2,
      nightScore: 3
    }

    const getScoreColor = () => "bg-red-500"
    const getScoreLabel = () => "High"

    cy.mount(ContextDataFactorRow, {
      props: {
        factor: vulnerabilityFactor,
        variant: "vulnerability",
        getScoreColor,
        getScoreLabel
      }
    })

    cy.get('[data-cy="vulnerability-context-data-score"]').should("have.length", 2)
    cy.get('[data-cy="vulnerability-context-data-2"]').should("exist")
    cy.get('[data-cy="vulnerability-context-data-3"]').should("exist")
  })

  it("renders vulnerability factor with null scores", () => {
    const vulnerabilityFactor: ContextDataVulnerabilityFactor = {
      ...baseFactor,
      factorId: "heat",
      dayScore: null,
      nightScore: null
    }

    const getScoreColor = () => "bg-red-500"
    const getScoreLabel = () => "High"

    cy.mount(ContextDataFactorRow, {
      props: {
        factor: vulnerabilityFactor,
        variant: "vulnerability",
        getScoreColor,
        getScoreLabel
      }
    })

    cy.get('[data-cy="vulnerability-context-data-score"]').should("have.length", 2)
    cy.contains("-").should("exist")
  })
})
