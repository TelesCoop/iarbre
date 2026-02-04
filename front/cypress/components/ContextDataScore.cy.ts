import ContextDataScore from "@/components/contextData/shared/ContextDataScore.vue"

describe("ContextDataScore.vue", () => {
  it("renders with correct score", () => {
    cy.mount(ContextDataScore, {
      props: {
        score: 7,
        maxScore: 10,
        percentage: 70,
        label: "plantabilité",
        colorScheme: "plantability"
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "7/10")
    cy.get('[data-cy="circular-progress"]').should("exist")
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
      }
    })

    cy.contains("Chaleur").should("be.visible")
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
      }
    })

    cy.get('[data-cy="context-data-score"]').should("contain", "75/100")
    cy.contains("points").should("be.visible")
  })
})
