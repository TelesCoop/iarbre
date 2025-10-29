import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import ContextDataScore from "@/components/contextData/shared/ContextDataScore.vue"
import CircularProgress from "@/components/progress/CircularProgress.vue"

describe("PlantabilityContextDataScore.vue", () => {
  beforeEach(() => {
    cy.mount(PlantabilityContextDataScore, {
      props: {
        score: 7,
        percentage: 70
      },
      global: {
        components: {
          ContextDataScore,
          CircularProgress
        }
      }
    })
  })

  it("renders with correct score and percentage", () => {
    cy.get('[data-cy="context-data-score"]').should("exist")
  })

  it("displays plantability label", () => {
    cy.contains("plantabilité").should("exist")
  })

  it("passes correct score to ContextDataScore", () => {
    cy.mount(PlantabilityContextDataScore, {
      props: {
        score: 8,
        percentage: 80
      },
      global: {
        components: {
          ContextDataScore,
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("exist")
  })

  it("handles low score", () => {
    cy.mount(PlantabilityContextDataScore, {
      props: {
        score: 2,
        percentage: 20
      },
      global: {
        components: {
          ContextDataScore,
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("exist")
  })

  it("handles maximum score", () => {
    cy.mount(PlantabilityContextDataScore, {
      props: {
        score: 10,
        percentage: 100
      },
      global: {
        components: {
          ContextDataScore,
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("exist")
  })

  it("handles zero score", () => {
    cy.mount(PlantabilityContextDataScore, {
      props: {
        score: 0,
        percentage: 0
      },
      global: {
        components: {
          ContextDataScore,
          CircularProgress
        }
      }
    })

    cy.get('[data-cy="context-data-score"]').should("exist")
  })
})
