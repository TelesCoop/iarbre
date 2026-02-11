/// <reference types="cypress" />
import ContextDataAccordionItem from "@/components/contextData/shared/ContextDataAccordionItem.vue"

describe("ContextDataAccordionItem", () => {
  it("renders accordion with label", () => {
    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "test-category",
          label: "Test Category",
          icon: "🧪",
          factors: [],
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.contains("Test Category").should("exist")
    cy.get('[data-cy="category-test-category"]').should("exist")
  })

  it("displays factors in table", () => {
    const mockFactors = [
      { key: "factor-1", label: "Factor 1", value: "60", icon: "📊" },
      { key: "factor-2", label: "Factor 2", value: "40", icon: "📈" }
    ]

    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "test-category",
          label: "Test Category",
          icon: "🧪",
          factors: mockFactors,
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".accordion-header").click()
    cy.contains("Factor 1").should("be.visible")
    cy.contains("Factor 2").should("be.visible")
    cy.contains("60").should("be.visible")
    cy.contains("40").should("be.visible")
  })

  it("displays multiple factors", () => {
    const mockFactors = [
      { key: "factor-a", label: "Factor A", value: "80", icon: "📊" },
      { key: "factor-b", label: "Factor B", value: "60", icon: "📈" },
      { key: "factor-c", label: "Factor C", value: "40", icon: "📉" }
    ]

    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "test-category",
          label: "Test Category",
          icon: "🧪",
          factors: mockFactors,
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".accordion-header").click()
    cy.contains("Factor A").should("be.visible")
    cy.contains("Factor B").should("be.visible")
    cy.contains("Factor C").should("be.visible")
    cy.get('[data-cy="factor-factor-a"]').should("exist")
    cy.get('[data-cy="factor-factor-b"]').should("exist")
    cy.get('[data-cy="factor-factor-c"]').should("exist")
  })

  it("handles empty factors array", () => {
    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "empty-category",
          label: "Empty Category",
          icon: "📭",
          factors: [],
          hasPositiveImpact: false,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.contains("Empty Category").should("exist")
    cy.get("tbody tr").should("have.length", 0)
  })

  it("displays positive impact styling", () => {
    const mockFactors = [
      { key: "factor-1", label: "Factor 1", value: "60", icon: "📊", impact: "positive" }
    ]

    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "positive-category",
          label: "Positive Impact",
          icon: "✅",
          factors: mockFactors,
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".impact-positive").should("exist")
  })

  it("displays negative impact styling", () => {
    const mockFactors = [
      { key: "factor-1", label: "Factor 1", value: "60", icon: "📊", impact: "negative" }
    ]

    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "negative-category",
          label: "Negative Impact",
          icon: "❌",
          factors: mockFactors,
          hasPositiveImpact: false,
          hasNegativeImpact: true
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".impact-negative").should("exist")
  })

  it("displays factor with unit", () => {
    const mockFactors = [
      { key: "factor-1", label: "Surface", value: "100", unit: "m²", icon: "📏" }
    ]

    cy.mount(ContextDataAccordionItem, {
      props: {
        group: {
          category: "test-category",
          label: "Test Category",
          icon: "🧪",
          factors: mockFactors,
          hasPositiveImpact: false,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.contains("100").should("exist")
    cy.contains("m²").should("exist")
  })
})
