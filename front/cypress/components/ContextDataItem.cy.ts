import ContextDataItem from "@/components/contextData/shared/ContextDataItem.vue"
import type { ContextDataFactor, ContextDataVulnerabilityFactor } from "@/types/contextData"

describe("ContextDataItem.vue", () => {
  const baseFactor: ContextDataFactor = {
    key: "test-factor",
    label: "Test Factor",
    value: "50",
    unit: "%",
    icon: "🌡️",
    description: "Test description"
  }

  it("renders basic factor with all props", () => {
    cy.mount(ContextDataItem, {
      props: {
        item: baseFactor
      }
    })

    cy.contains("Test Factor").should("be.visible")
    cy.contains("50").should("be.visible")
    cy.contains("%").should("be.visible")
    cy.contains("🌡️").should("be.visible")
    cy.contains("Test description").should("be.visible")
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

    cy.mount(ContextDataItem, {
      props: {
        item: vulnerabilityFactor,
        colorScheme: "vulnerability",
        getScoreColor,
        getScoreLabel
      }
    })

    cy.contains("☀️ Jour").should("be.visible")
    cy.contains("🌙 Nuit").should("be.visible")
    cy.get('[data-cy="vulnerability-context-data-score"]').should("have.length", 2)
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

    cy.mount(ContextDataItem, {
      props: {
        item: vulnerabilityFactor,
        colorScheme: "vulnerability",
        getScoreColor,
        getScoreLabel
      }
    })

    cy.contains("☀️ Jour").should("be.visible")
    cy.contains("🌙 Nuit").should("be.visible")
  })
})
