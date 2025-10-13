import ContextDataItem from "@/components/contextData/shared/ContextDataItem.vue"
import VulnerabilityContextDataScore from "@/components/contextData/vulnerability/VulnerabilityContextDataScore.vue"
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

  it("renders without icon", () => {
    const factorWithoutIcon = { ...baseFactor, icon: undefined }

    cy.mount(ContextDataItem, {
      props: {
        item: factorWithoutIcon
      }
    })

    cy.contains("Test Factor").should("be.visible")
    cy.get('[data-cy="factor-icon"]').should("not.exist")
  })

  it("renders without description", () => {
    const factorWithoutDescription = { ...baseFactor, description: undefined }

    cy.mount(ContextDataItem, {
      props: {
        item: factorWithoutDescription
      }
    })

    cy.contains("Test Factor").should("be.visible")
    cy.contains("Test description").should("not.exist")
  })

  it("renders without unit", () => {
    const factorWithoutUnit = { ...baseFactor, unit: undefined }

    cy.mount(ContextDataItem, {
      props: {
        item: factorWithoutUnit
      }
    })

    cy.contains("Test Factor").should("be.visible")
    cy.contains("50").should("be.visible")
    cy.contains("%").should("not.exist")
  })

  it("applies plantability color scheme for positive impact", () => {
    const positiveFactor = { ...baseFactor, impact: "positive" as const }

    cy.mount(ContextDataItem, {
      props: {
        item: positiveFactor,
        colorScheme: "plantability"
      }
    })

    cy.get('[data-cy="factor-icon"]').should("have.class", "bg-green-100")
    cy.get('[data-cy="factor-icon"]').should("have.class", "text-green-700")
  })

  it("applies plantability color scheme for negative impact", () => {
    const negativeFactor = { ...baseFactor, impact: "negative" as const }

    cy.mount(ContextDataItem, {
      props: {
        item: negativeFactor,
        colorScheme: "plantability"
      }
    })

    cy.get('[data-cy="factor-icon"]').should("have.class", "bg-orange-100")
    cy.get('[data-cy="factor-icon"]').should("have.class", "text-orange-700")
  })

  it("applies climate color scheme", () => {
    cy.mount(ContextDataItem, {
      props: {
        item: baseFactor,
        colorScheme: "climate"
      }
    })

    cy.get('[data-cy="factor-icon"]').should("have.class", "bg-primary-100")
    cy.get('[data-cy="factor-icon"]').should("have.class", "text-primary-700")
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
      },
      global: {
        components: {
          VulnerabilityContextDataScore
        }
      }
    })

    cy.contains("☀️ Jour:").should("be.visible")
    cy.contains("🌙 Nuit:").should("be.visible")
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
      },
      global: {
        components: {
          VulnerabilityContextDataScore
        }
      }
    })

    cy.contains("☀️ Jour:").should("be.visible")
    cy.contains("🌙 Nuit:").should("be.visible")
  })

  it("has correct accessibility attributes", () => {
    cy.mount(ContextDataItem, {
      props: {
        item: baseFactor
      }
    })

    cy.get('[role="listitem"]').should("exist")
    cy.get('[data-cy="factor-icon"]').should("have.attr", "aria-label", "Icône pour Test Factor")
  })
})
