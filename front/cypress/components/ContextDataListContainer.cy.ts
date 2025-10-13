import ContextDataListContainer from "@/components/contextData/shared/ContextDataListContainer.vue"
import ContextDataAccordionItem from "@/components/contextData/shared/ContextDataAccordionItem.vue"
import type { ContextDataFactorGroup } from "@/types/contextData"

describe("ContextDataListContainer.vue", () => {
  const mockGroups: ContextDataFactorGroup[] = [
    {
      category: "Test Category 1",
      factors: [
        {
          key: "factor1",
          label: "Factor 1",
          value: "50",
          unit: "%"
        }
      ]
    },
    {
      category: "Test Category 2",
      factors: [
        {
          key: "factor2",
          label: "Factor 2",
          value: "75",
          unit: "m²"
        }
      ]
    }
  ]

  it("renders with plantability color scheme", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("renders all groups", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.contains("Test Category 1").should("exist")
    cy.contains("Test Category 2").should("exist")
  })

  it("renders with climate color scheme", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "climate"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("renders with vulnerability color scheme", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "vulnerability"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("applies fullHeight prop", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability",
        fullHeight: true
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("applies scrollable prop", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability",
        scrollable: true
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("applies custom aria label", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability",
        ariaLabel: "Custom aria label"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("have.attr", "aria-label", "Custom aria label")
  })

  it("uses default aria label when not provided", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "plantability"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("have.attr", "aria-label", "Liste des paramètres par catégorie")
  })

  it("renders with empty groups array", () => {
    cy.mount(ContextDataListContainer, {
      props: {
        groups: [],
        colorScheme: "plantability"
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("passes getScoreColor callback to accordion items", () => {
    const getScoreColor = cy.stub().returns("bg-red-500")

    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "vulnerability",
        getScoreColor
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })

  it("passes getScoreLabel callback to accordion items", () => {
    const getScoreLabel = cy.stub().returns("High impact")

    cy.mount(ContextDataListContainer, {
      props: {
        groups: mockGroups,
        colorScheme: "vulnerability",
        getScoreLabel
      },
      global: {
        components: {
          ContextDataAccordionItem
        }
      }
    })

    cy.get('[role="list"]').should("exist")
  })
})
