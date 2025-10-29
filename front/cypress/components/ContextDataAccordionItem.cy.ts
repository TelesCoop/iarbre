/// <reference types="cypress" />
import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import ContextDataAccordionItem from "@/components/contextData/shared/ContextDataAccordionItem.vue"

describe("ContextDataAccordionItem", () => {
  it("renders accordion with label", () => {
    const pinia = createPinia()

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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
  })

  it("expands on click", () => {
    const pinia = createPinia()
    const mockFactors = [
      { key: "factor-1", label: "Factor 1", value: "60", icon: "📊" },
      { key: "factor-2", label: "Factor 2", value: "40", icon: "📈" }
    ]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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

    cy.get('[data-cy="category-test-category"]').click()
    cy.contains("Factor 1").should("be.visible")
    cy.contains("Factor 2").should("be.visible")
  })

  it("collapses on second click", () => {
    const pinia = createPinia()
    const mockFactors = [{ key: "factor-1", label: "Factor 1", value: "60", icon: "📊" }]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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

    cy.get('[data-cy="category-test-category"]').click()
    cy.get("#category-test-category").should("exist")
    cy.contains("Factor 1").should("be.visible")

    cy.get('[data-cy="category-test-category"]').click()
    cy.get("#category-test-category").should("not.exist")
  })

  it("displays multiple factors", () => {
    const pinia = createPinia()
    const mockFactors = [
      { key: "factor-a", label: "Factor A", value: "80", icon: "📊" },
      { key: "factor-b", label: "Factor B", value: "60", icon: "📈" },
      { key: "factor-c", label: "Factor C", value: "40", icon: "📉" }
    ]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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

    cy.get('[data-cy="category-test-category"]').click()

    cy.contains("Factor A").should("be.visible")
    cy.contains("Factor B").should("be.visible")
    cy.contains("Factor C").should("be.visible")
  })

  it("handles empty factors array", () => {
    const pinia = createPinia()

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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
    cy.contains("0 paramètre").should("exist")
  })

  it("shows chevron down icon when collapsed", () => {
    const pinia = createPinia()
    const mockFactors = [{ key: "factor-1", label: "Factor", value: "50", icon: "📊" }]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
      props: {
        group: {
          category: "test-category",
          label: "Test",
          icon: "🧪",
          factors: mockFactors,
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".pi-chevron-down").should("exist")
  })

  it("shows chevron up icon when expanded", () => {
    const pinia = createPinia()
    const mockFactors = [{ key: "factor-1", label: "Factor", value: "50", icon: "📊" }]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
      props: {
        group: {
          category: "test-category",
          label: "Test",
          icon: "🧪",
          factors: mockFactors,
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get('[data-cy="category-test-category"]').click()
    cy.get(".pi-chevron-up").should("exist")
  })

  it("displays impact indicator for positive impact", () => {
    const pinia = createPinia()

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
      props: {
        group: {
          category: "positive-category",
          label: "Positive Impact",
          icon: "✅",
          factors: [],
          hasPositiveImpact: true,
          hasNegativeImpact: false
        },
        colorScheme: "plantability"
      }
    })

    cy.get(".bg-green-500").should("exist")
  })

  it("displays parameter count", () => {
    const pinia = createPinia()
    const mockFactors = [
      { key: "factor-1", label: "Factor 1", value: "60", icon: "📊" },
      { key: "factor-2", label: "Factor 2", value: "40", icon: "📈" },
      { key: "factor-3", label: "Factor 3", value: "50", icon: "📉" }
    ]

    mount(ContextDataAccordionItem, {
      global: {
        plugins: [pinia]
      },
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

    cy.contains("3 paramètres").should("exist")
  })
})
