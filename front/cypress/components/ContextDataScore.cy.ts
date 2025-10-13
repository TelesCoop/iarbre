import ContextDataScore from "@/components/contextData/shared/ContextDataScore.vue"
import CircularProgress from "@/components/progress/CircularProgress.vue"

describe("ContextDataScore.vue", () => {
  it("renders with plantability color scheme", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 7,
        maxScore: 10,
        percentage: 70,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "7/10")
    cy.get('[data-cy="circular-progress"]').should("exist")
  })

  it("renders with vulnerability color scheme", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 6,
        maxScore: 9,
        percentage: 66.67,
        label: "vulnérabilité",
        colorScheme: "vulnerability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "6/9")
  })

  it("renders with climate color scheme", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 5,
        maxScore: 10,
        percentage: 50,
        label: "climat",
        colorScheme: "climate"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "5/10")
  })

  it("renders with name prop", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 8,
        maxScore: 10,
        percentage: 80,
        label: "plantabilité",
        colorScheme: "plantability",
        name: "Chaleur"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.contains("Chaleur:").should("be.visible")
    cy.get('[data-cy="context-data-score"]').should("contain", "8/10")
  })

  it("renders without name prop", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 5,
        maxScore: 10,
        percentage: 50,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.contains("Score :").should("be.visible")
    cy.get('[data-cy="context-data-score"]').should("contain", "5/10")
  })

  it("renders with custom unit", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 75,
        maxScore: 100,
        percentage: 75,
        label: "performance",
        colorScheme: "plantability",
        unit: "points"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "75/100 points")
  })

  it("handles zero score", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 0,
        maxScore: 10,
        percentage: 0,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "0/10")
  })

  it("handles maximum score", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 10,
        maxScore: 10,
        percentage: 100,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "10/10")
  })

  it("has correct accessibility attributes", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 7,
        maxScore: 10,
        percentage: 70,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get("section").should("have.attr", "aria-labelledby")
    cy.get('[data-cy="circular-progress"]').should("have.attr", "aria-label")
  })

  it("renders screen reader only heading", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 7,
        maxScore: 10,
        percentage: 70,
        label: "plantabilité",
        colorScheme: "plantability"
      },
      global: {
        components: {
          CircularProgress
        }
      }
    })

    cy.get("h3").should("have.class", "sr-only")
  })
})
